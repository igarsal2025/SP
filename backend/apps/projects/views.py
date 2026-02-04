from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.audit.services import log_audit_event
from apps.accounts.mixins import CompanySitecQuerysetMixin
from apps.accounts.permissions import AccessPolicyPermission

from .models import Presupuesto, Proyecto, Riesgo, Tarea
from .serializers import (
    PresupuestoSerializer,
    ProyectoListSerializer,
    ProyectoSerializer,
    RiesgoSerializer,
    TareaSerializer,
)
from rest_framework.pagination import PageNumberPagination


class ProyectoViewSet(CompanySitecQuerysetMixin, viewsets.ModelViewSet):
    """ViewSet para proyectos"""
    queryset = Proyecto.objects.select_related(
        "company", "sitec", "project_manager", "supervisor"
    ).prefetch_related("technicians", "tareas", "riesgos", "presupuestos").all()
    permission_classes = [IsAuthenticated, AccessPolicyPermission]
    pagination_class = type(
        "ProyectoPagination",
        (PageNumberPagination,),
        {"page_size": 10, "page_size_query_param": "page_size", "max_page_size": 50},
    )

    def get_serializer_class(self):
        if self.action == "list":
            return ProyectoListSerializer
        return ProyectoSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtros adicionales
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        pm_id = self.request.query_params.get("project_manager")
        if pm_id:
            queryset = queryset.filter(project_manager_id=pm_id)

        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        proyecto = serializer.save(
            company=self.request.company,
            sitec=self.request.sitec,
        )
        log_audit_event(self.request, "proyecto_created", proyecto)

    def perform_update(self, serializer):
        proyecto = serializer.save()
        
        # Validación adicional: Si se completa, verificar que todas las tareas estén completadas
        if proyecto.status == "completed":
            tareas_no_completadas = proyecto.tareas.exclude(status="completed")
            if tareas_no_completadas.exists():
                from rest_framework.exceptions import ValidationError
                raise ValidationError({
                    "status": f"No se puede completar el proyecto. Hay {tareas_no_completadas.count()} tarea(s) no completada(s): {', '.join([t.title for t in tareas_no_completadas[:5]])}"
                })
        
        log_audit_event(self.request, "proyecto_updated", proyecto)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Completar proyecto"""
        proyecto = self.get_object()
        if proyecto.status == "completed":
            return Response(
                {"error": "Proyecto ya está completado"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Validación: Verificar que todas las tareas estén completadas
        tareas_no_completadas = proyecto.tareas.exclude(status="completed")
        if tareas_no_completadas.exists():
            return Response(
                {
                    "error": f"No se puede completar el proyecto. Hay {tareas_no_completadas.count()} tarea(s) no completada(s)",
                    "tareas_pendientes": [{"id": str(t.id), "title": t.title, "status": t.status} for t in tareas_no_completadas]
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        from django.utils import timezone
        proyecto.status = "completed"
        proyecto.completed_at = timezone.now()
        proyecto.progress_pct = 100
        proyecto.save()

        log_audit_event(request, "proyecto_completed", proyecto)
        return Response(ProyectoSerializer(proyecto).data)


class TareaViewSet(viewsets.ModelViewSet):
    """ViewSet para tareas"""
    queryset = Tarea.objects.select_related("project", "assigned_to").all()
    serializer_class = TareaSerializer
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset.filter(project__company=self.request.company)
    
    def perform_create(self, serializer):
        """Validar que no se creen tareas en proyecto cancelado"""
        project = serializer.validated_data.get('project')
        if project and project.status == "cancelled":
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                "project": "No se pueden crear tareas en un proyecto cancelado"
            })
        serializer.save()

    def perform_update(self, serializer):
        tarea = serializer.save()
        if tarea.status == "completed" and tarea.completed_at is None:
            from django.utils import timezone
            tarea.completed_at = timezone.now()
            tarea.save(update_fields=["completed_at"])
        log_audit_event(self.request, "tarea_updated", tarea)


class RiesgoViewSet(viewsets.ModelViewSet):
    """ViewSet para riesgos"""
    queryset = Riesgo.objects.select_related("project").all()
    serializer_class = RiesgoSerializer
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset.filter(project__company=self.request.company)


class PresupuestoViewSet(viewsets.ModelViewSet):
    """ViewSet para presupuestos"""
    queryset = Presupuesto.objects.select_related("project").all()
    serializer_class = PresupuestoSerializer
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset.filter(project__company=self.request.company)
