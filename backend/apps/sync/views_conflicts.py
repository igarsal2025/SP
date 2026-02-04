"""
Vistas para resolución avanzada de conflictos con diffs visuales
"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import AccessPolicyPermission

from .models import SyncItem, SyncSession
from .serializers import SyncItemSerializer


class ConflictDiffView(APIView):
    """Endpoint para obtener diffs visuales de conflictos"""
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get(self, request, session_id, item_id):
        """Obtener diff visual de un conflicto"""
        company = request.company
        sitec = request.sitec
        
        try:
            session = SyncSession.objects.get(
                id=session_id,
                company=company,
                sitec=sitec,
                user=request.user
            )
        except SyncSession.DoesNotExist:
            return Response(
                {"error": "Sesión no encontrada"},
                status=404
            )
        
        try:
            item = SyncItem.objects.get(
                id=item_id,
                session=session,
                status="conflict"
            )
        except SyncItem.DoesNotExist:
            return Response(
                {"error": "Item de conflicto no encontrado"},
                status=404
            )
        
        # Obtener datos del servidor (desde item existente o snapshot)
        server_data = item.data or {}
        
        # Obtener datos del cliente (desde el request o item)
        client_data = request.query_params.get("client_data")
        if client_data:
            import json
            try:
                client_data = json.loads(client_data)
            except:
                client_data = {}
        else:
            client_data = item.data or {}
        
        # Calcular diff
        diff = self._calculate_diff(server_data, client_data, item.entity_type)
        
        return Response({
            "entity_type": item.entity_type,
            "entity_id": item.entity_id,
            "server_data": server_data,
            "client_data": client_data,
            "diff": diff,
            "server_timestamp": item.server_timestamp.isoformat() if item.server_timestamp else None,
            "client_timestamp": item.client_timestamp.isoformat() if item.client_timestamp else None,
        })
    
    def _calculate_diff(self, server_data, client_data, entity_type):
        """Calcular diferencias entre datos del servidor y cliente"""
        diff = {
            "added": {},
            "removed": {},
            "modified": {},
            "unchanged": {}
        }
        
        if not isinstance(server_data, dict) or not isinstance(client_data, dict):
            return diff
        
        # Campos agregados en cliente
        for key in client_data:
            if key not in server_data:
                diff["added"][key] = {
                    "client": client_data[key],
                    "server": None
                }
        
        # Campos removidos en cliente
        for key in server_data:
            if key not in client_data:
                diff["removed"][key] = {
                    "client": None,
                    "server": server_data[key]
                }
        
        # Campos modificados
        for key in server_data:
            if key in client_data:
                server_value = server_data[key]
                client_value = client_data[key]
                
                if server_value != client_value:
                    diff["modified"][key] = {
                        "client": client_value,
                        "server": server_value
                    }
                else:
                    diff["unchanged"][key] = server_value
        
        return diff


class ConflictResolutionView(APIView):
    """Endpoint para resolver conflictos con resolución granular"""
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def post(self, request, session_id, item_id):
        """Resolver conflicto con resolución por campo"""
        company = request.company
        sitec = request.sitec
        
        try:
            session = SyncSession.objects.get(
                id=session_id,
                company=company,
                sitec=sitec,
                user=request.user
            )
        except SyncSession.DoesNotExist:
            return Response(
                {"error": "Sesión no encontrada"},
                status=404
            )
        
        try:
            item = SyncItem.objects.get(
                id=item_id,
                session=session,
                status="conflict"
            )
        except SyncItem.DoesNotExist:
            return Response(
                {"error": "Item de conflicto no encontrado"},
                status=404
            )
        
        # Obtener resolución
        resolution = request.data.get("resolution", {})
        # Formato: {"field_name": "server"|"client"|"merge", ...}
        
        # Obtener datos
        server_data = item.data or {}
        client_data = request.data.get("client_data", {})
        
        # Aplicar resolución
        resolved_data = self._apply_resolution(server_data, client_data, resolution)
        
        # Actualizar item
        item.data = resolved_data
        item.status = "synced"
        item.save()
        
        # Actualizar sesión si no hay más conflictos
        remaining_conflicts = SyncItem.objects.filter(
            session=session,
            status="conflict"
        ).count()
        
        if remaining_conflicts == 0:
            session.status = "completed"
            session.save()
        
        return Response({
            "item": SyncItemSerializer(item).data,
            "resolved_data": resolved_data
        })
    
    def _apply_resolution(self, server_data, client_data, resolution):
        """Aplicar resolución por campo"""
        resolved = {}
        
        # Empezar con datos del servidor
        resolved.update(server_data)
        
        # Aplicar resoluciones específicas
        for field, choice in resolution.items():
            if choice == "server":
                if field in server_data:
                    resolved[field] = server_data[field]
            elif choice == "client":
                if field in client_data:
                    resolved[field] = client_data[field]
            elif choice == "merge":
                # Merge: combinar si son objetos, o usar cliente
                if isinstance(server_data.get(field), dict) and isinstance(client_data.get(field), dict):
                    resolved[field] = {**server_data.get(field, {}), **client_data.get(field, {})}
                elif isinstance(server_data.get(field), list) and isinstance(client_data.get(field), list):
                    resolved[field] = list(set(server_data.get(field, []) + client_data.get(field, [])))
                else:
                    resolved[field] = client_data.get(field)
        
        # Agregar campos nuevos del cliente que no están en resolución
        for field in client_data:
            if field not in resolution and field not in server_data:
                resolved[field] = client_data[field]
        
        return resolved
