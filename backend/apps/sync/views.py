from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import log_audit_event
from apps.accounts.permissions import AccessPolicyPermission

from .models import SyncItem, SyncSession
from .serializers import (
    SyncItemSerializer,
    SyncRequestSerializer,
    SyncResponseSerializer,
    SyncSessionSerializer,
)


class SyncView(APIView):
    """Endpoint principal de sincronización"""
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    ENTITY_MERGE_RULES = {
        "report": {
            "server_fields": {
                "status",
                "signature_tech",
                "signature_supervisor",
                "signature_date",
                "submitted_at",
                "approved_at",
                "qa_signed",
                "rules_version",
                "riesgo_score",
                "sugerencias_ia",
                "predicciones",
                "wizard_schema_version",
                "wizard_updated_at",
                "wizard_client_id",
            },
            "merge_fields": {"wizard_data", "metadata"},
        },
        "project": {
            "server_fields": {
                "status",
                "priority",
                "progress_pct",
                "completed_at",
                "project_manager",
                "supervisor",
                "technicians",
                "riesgo_score",
                "sugerencias_ia",
                "predicciones",
            },
            "merge_fields": {"metadata"},
            "list_merge_fields": {"tags"},
        },
        "tarea": {
            "server_fields": {"status", "completed_at"},
            "merge_fields": {"metadata"},
        },
        "task": {
            "server_fields": {"status", "completed_at"},
            "merge_fields": {"metadata"},
        },
        "riesgo": {
            "server_fields": {"severity", "probability", "mitigation_status", "resolved", "resolved_at"},
            "merge_fields": {"metadata"},
        },
        "risk": {
            "server_fields": {"severity", "probability", "mitigation_status", "resolved", "resolved_at"},
            "merge_fields": {"metadata"},
        },
        "incidente": {
            "server_fields": {"severity", "resolved", "resolved_at"},
            "merge_fields": {"metadata"},
        },
        "incident": {
            "server_fields": {"severity", "resolved", "resolved_at"},
            "merge_fields": {"metadata"},
        },
        "evidencia": {
            "server_fields": {"file_path", "file_name", "file_size", "mime_type"},
            "merge_fields": {"metadata"},
        },
        "evidence": {
            "server_fields": {"file_path", "file_name", "file_size", "mime_type"},
            "merge_fields": {"metadata"},
        },
    }

    def _is_empty_value(self, value):
        return value in (None, "", [], {})

    def _merge_payload(self, server_data, client_data, entity_type, resolution_payload):
        if entity_type == "wizard_step" and isinstance(server_data, dict) and isinstance(client_data, dict):
            merged = {**server_data}
            for key, value in client_data.items():
                if value not in (None, "", []):
                    merged[key] = value
            return merged
        rules = self.ENTITY_MERGE_RULES.get(entity_type)
        if rules and isinstance(server_data, dict) and isinstance(client_data, dict):
            merged = {**server_data}
            server_fields = rules.get("server_fields", set())
            merge_fields = rules.get("merge_fields", set())
            list_merge_fields = rules.get("list_merge_fields", set())
            for key, value in client_data.items():
                if key in server_fields:
                    continue
                if key in merge_fields and isinstance(value, dict) and isinstance(server_data.get(key), dict):
                    merged[key] = {**server_data.get(key, {}), **value}
                    continue
                if key in list_merge_fields and isinstance(value, list):
                    merged[key] = list(dict.fromkeys((server_data.get(key) or []) + value))
                    continue
                if not self._is_empty_value(value):
                    merged[key] = value
            return merged
        if isinstance(resolution_payload, dict) and resolution_payload.get("mode") == "merge":
            fields = resolution_payload.get("fields", {})
            merged = {}
            if isinstance(server_data, dict):
                merged.update(server_data)
            if isinstance(client_data, dict):
                merged.update(client_data)
            for field, choice in fields.items():
                if choice == "server" and isinstance(server_data, dict):
                    merged[field] = server_data.get(field)
                elif choice == "client" and isinstance(client_data, dict):
                    merged[field] = client_data.get(field)
            return merged
        return client_data

    def post(self, request):
        serializer = SyncRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        items_data = serializer.validated_data.get("items", [])
        resolution = serializer.validated_data.get("resolution", {})
        session_id = serializer.validated_data.get("session_id")

        # Obtener o crear sesión de sync
        if session_id:
            try:
                session = SyncSession.objects.get(
                    id=session_id,
                    company=request.company,
                    user=request.user,
                )
            except SyncSession.DoesNotExist:
                return Response(
                    {"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND
                )
        else:
            session = SyncSession.objects.create(
                company=request.company,
                sitec=request.sitec,
                user=request.user,
                status="syncing",
            )

        synced_items = []
        conflicts = []

        # Procesar cada item
        for item_data in items_data:
            entity_type = item_data.get("entity_type", "wizard_step")
            entity_id = item_data.get("entity_id") or item_data.get("step")
            data = item_data.get("data", {})
            client_timestamp = item_data.get("updatedAt") or item_data.get("client_timestamp")

            # Verificar resolución explícita
            resolution_key = str(entity_id) or entity_type
            choice = resolution.get(resolution_key) or resolution.get(entity_id)

            # Buscar item existente (de otras sesiones del mismo usuario)
            existing_item = SyncItem.objects.filter(
                session__company=request.company,
                session__user=request.user,
                entity_type=entity_type,
                entity_id=str(entity_id),
            ).exclude(session=session).order_by("-server_timestamp").first()

            sync_item, created = SyncItem.objects.get_or_create(
                session=session,
                entity_type=entity_type,
                entity_id=str(entity_id),
                defaults={
                    "status": "pending",
                    "data": data,
                    "client_timestamp": client_timestamp,
                },
            )
            if not created:
                sync_item.data = data
                sync_item.client_timestamp = client_timestamp

            # Procesar según resolución o detección de conflictos
            if choice == "server" and existing_item:
                sync_item.data = existing_item.data
                sync_item.server_timestamp = existing_item.server_timestamp
                sync_item.status = "synced"
            elif choice == "client":
                sync_item.data = data
                sync_item.client_timestamp = client_timestamp
                sync_item.status = "synced"
            elif isinstance(choice, dict) and choice.get("mode") == "merge" and existing_item:
                merged = self._merge_payload(existing_item.data, data, entity_type, choice)
                sync_item.data = merged
                sync_item.status = "synced"
            elif existing_item and client_timestamp and existing_item.server_timestamp:
                # Detectar conflicto por timestamp
                from django.utils.dateparse import parse_datetime
                from django.utils import timezone
                
                if isinstance(client_timestamp, str):
                    client_dt = parse_datetime(client_timestamp)
                    if client_dt:
                        client_dt = timezone.make_aware(client_dt) if timezone.is_naive(client_dt) else client_dt
                else:
                    client_dt = client_timestamp
                
                if client_dt and existing_item.server_timestamp and client_dt < existing_item.server_timestamp:
                    conflicts.append(f"{entity_type}_{entity_id}")
                    sync_item.status = "conflict"
                    continue

            # Sincronizar exitosamente
            sync_item.status = "synced"
            sync_item.server_timestamp = sync_item.updated_at
            sync_item.save()
            synced_items.append(sync_item)

        # Actualizar estadísticas de sesión
        session.items_synced = len(synced_items)
        session.conflicts_detected = len(conflicts)
        session.items_failed = len(items_data) - len(synced_items) - len(conflicts)

        if conflicts:
            session.status = "conflict"
        elif session.items_failed > 0:
            session.status = "failed"
        else:
            session.status = "completed"
            from django.utils import timezone
            session.completed_at = timezone.now()

        session.save()

        # Auditoría
        log_audit_event(request, "sync_completed", session)

        response_data = {
            "session": SyncSessionSerializer(session).data,
            "synced_items": SyncItemSerializer(synced_items, many=True).data,
            "conflicts": conflicts,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class SyncSessionView(APIView):
    """Endpoint para consultar sesiones de sincronización"""
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get(self, request, session_id=None):
        if session_id:
            try:
                session = SyncSession.objects.get(
                    id=session_id,
                    company=request.company,
                    user=request.user,
                )
                return Response(SyncSessionSerializer(session).data)
            except SyncSession.DoesNotExist:
                return Response(
                    {"error": "Session not found"}, status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Listar sesiones del usuario
            sessions = SyncSession.objects.filter(
                company=request.company,
                user=request.user,
            ).order_by("-started_at")[:50]
            return Response(SyncSessionSerializer(sessions, many=True).data)
