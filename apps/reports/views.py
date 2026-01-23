from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from apps.audit.services import log_audit_event
from apps.accounts.mixins import CompanySitecQuerysetMixin
from apps.accounts.permissions import AccessPolicyPermission

from .models import Evidencia, Incidente, ReporteSemanal
from .serializers import (
    EvidenciaSerializer,
    IncidenteSerializer,
    ReporteSemanalListSerializer,
    ReporteSemanalSerializer,
)


class ReporteSemanalViewSet(CompanySitecQuerysetMixin, viewsets.ModelViewSet):
    """ViewSet para reportes semanales"""
    queryset = ReporteSemanal.objects.select_related(
        "company", "sitec", "technician", "supervisor", "project"
    ).prefetch_related("evidencias", "incidentes").all()
    permission_classes = [IsAuthenticated, AccessPolicyPermission]
    pagination_class = type(
        "ReportePagination",
        (PageNumberPagination,),
        {"page_size": 10, "page_size_query_param": "page_size", "max_page_size": 50},
    )

    def get_serializer_class(self):
        if self.action == "list":
            return ReporteSemanalListSerializer
        return ReporteSemanalSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtros adicionales
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        week_start = self.request.query_params.get("week_start")
        if week_start:
            queryset = queryset.filter(week_start=week_start)

        technician_id = self.request.query_params.get("technician")
        if technician_id:
            queryset = queryset.filter(technician_id=technician_id)

        return queryset.order_by("-week_start", "-created_at")

    def perform_create(self, serializer):
        reporte = serializer.save(
            company=self.request.company,
            sitec=self.request.sitec,
            technician=self.request.user,
        )
        log_audit_event(self.request, "reporte_created", reporte)

    def perform_update(self, serializer):
        reporte = serializer.save()
        log_audit_event(self.request, "reporte_updated", reporte)

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        """Enviar reporte para aprobación"""
        reporte = self.get_object()
        if reporte.status != "draft":
            return Response(
                {"error": "Solo reportes en borrador pueden enviarse"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from django.utils import timezone
        reporte.status = "submitted"
        reporte.submitted_at = timezone.now()
        reporte.save()

        log_audit_event(request, "reporte_submitted", reporte)
        return Response(ReporteSemanalSerializer(reporte).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Aprobar reporte (solo supervisor/admin)"""
        reporte = self.get_object()
        if reporte.status != "submitted":
            return Response(
                {"error": "Solo reportes enviados pueden aprobarse"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from django.utils import timezone
        reporte.status = "approved"
        reporte.approved_at = timezone.now()
        reporte.supervisor = request.user
        reporte.save()

        log_audit_event(request, "reporte_approved", reporte)
        return Response(ReporteSemanalSerializer(reporte).data)

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Rechazar reporte (solo supervisor/admin)"""
        reporte = self.get_object()
        if reporte.status != "submitted":
            return Response(
                {"error": "Solo reportes enviados pueden rechazarse"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reason = request.data.get("reason", "")
        from django.utils import timezone
        reporte.status = "rejected"
        reporte.rejected_at = timezone.now()
        reporte.supervisor = request.user
        # Guardar razón de rechazo en metadata
        if not reporte.metadata:
            reporte.metadata = {}
        reporte.metadata["rejection_reason"] = reason
        reporte.metadata["rejected_by"] = str(request.user.id)
        reporte.save()

        log_audit_event(request, "reporte_rejected", reporte, extra_data={"reason": reason})
        return Response(ReporteSemanalSerializer(reporte).data)


class EvidenciaViewSet(viewsets.ModelViewSet):
    """ViewSet para evidencias"""
    queryset = Evidencia.objects.select_related("reporte").all()
    serializer_class = EvidenciaSerializer
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        reporte_id = self.request.query_params.get("reporte")
        if reporte_id:
            queryset = queryset.filter(reporte_id=reporte_id)
        return queryset.filter(reporte__company=self.request.company)


class IncidenteViewSet(viewsets.ModelViewSet):
    """ViewSet para incidentes"""
    queryset = Incidente.objects.select_related("reporte").all()
    serializer_class = IncidenteSerializer
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        reporte_id = self.request.query_params.get("reporte")
        if reporte_id:
            queryset = queryset.filter(reporte_id=reporte_id)
        return queryset.filter(reporte__company=self.request.company)

    def perform_update(self, serializer):
        incidente = serializer.save()
        if incidente.resolved and incidente.resolved_at is None:
            from django.utils import timezone
            incidente.resolved_at = timezone.now()
            incidente.save(update_fields=["resolved_at"])
        log_audit_event(self.request, "incidente_updated", incidente)