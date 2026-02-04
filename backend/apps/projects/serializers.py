from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import Presupuesto, Proyecto, Riesgo, Tarea


class TareaSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Tarea
        fields = [
            "id",
            "project",
            "title",
            "description",
            "status",
            "priority",
            "assigned_to",
            "due_date",
            "completed_at",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "company",
            "sitec",
            "created_at",
            "updated_at",
            "completed_at",
        ]

    def validate(self, data):
        """Validaciones de lógica de negocio para tareas"""
        instance = self.instance
        project = data.get('project') or (instance.project if instance else None)
        status = data.get('status', instance.status if instance else None)
        due_date = data.get('due_date', instance.due_date if instance else None)
        
        # Validación: No se pueden crear tareas en proyecto cancelado
        if project and project.status == "cancelled":
            if not instance:  # Creación nueva
                raise serializers.ValidationError({
                    "project": "No se pueden crear tareas en un proyecto cancelado"
                })
        
        # Validación: due_date debe ser >= start_date del proyecto
        if due_date and project:
            if due_date < project.start_date:
                raise serializers.ValidationError({
                    "due_date": f"La fecha de vencimiento ({due_date}) debe ser posterior o igual a la fecha de inicio del proyecto ({project.start_date})"
                })
        
        # Validación: Tarea blocked no puede cambiar directamente a completed
        if instance and instance.status == "blocked" and status == "completed":
            raise serializers.ValidationError({
                "status": "Una tarea bloqueada no puede cambiar directamente a completada. Debe desbloquearse primero (pending/in_progress)"
            })
        
        # Validación: Si se completa, establecer completed_at
        if status == "completed" and instance:
            if not instance.completed_at:
                data['completed_at'] = timezone.now()
        
        return data


class RiesgoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Riesgo
        fields = [
            "id",
            "project",
            "title",
            "description",
            "severity",
            "probability",
            "mitigation_plan",
            "mitigation_status",
            "riesgo_score",
            "sugerencias_ia",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PresupuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presupuesto
        fields = [
            "id",
            "project",
            "category",
            "description",
            "amount_estimated",
            "amount_actual",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


User = get_user_model()


class ProyectoSerializer(serializers.ModelSerializer):
    project_manager = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    supervisor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    technicians = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, required=False
    )
    tareas = TareaSerializer(many=True, read_only=True)
    riesgos = RiesgoSerializer(many=True, read_only=True)
    presupuestos = PresupuestoSerializer(many=True, read_only=True)

    class Meta:
        model = Proyecto
        fields = [
            "id",
            "company",
            "sitec",
            "name",
            "code",
            "description",
            "site_address",
            "client_name",
            "client_contact",
            "start_date",
            "end_date",
            "estimated_end_date",
            "project_manager",
            "supervisor",
            "technicians",
            "status",
            "priority",
            "progress_pct",
            "budget_estimated",
            "budget_actual",
            "riesgo_score",
            "sugerencias_ia",
            "predicciones",
            "metadata",
            "tags",
            "tareas",
            "riesgos",
            "presupuestos",
            "created_at",
            "updated_at",
            "completed_at",
        ]
        read_only_fields = [
            "id",
            "company",
            "sitec",
            "created_at",
            "updated_at",
            "completed_at",
        ]

    def validate(self, data):
        """Validaciones estrictas de lógica de negocio para proyectos"""
        instance = self.instance
        status = data.get('status', instance.status if instance else 'planning')
        progress_pct = data.get('progress_pct', instance.progress_pct if instance else 0)
        project_manager = data.get('project_manager', instance.project_manager if instance else None)
        end_date = data.get('end_date', instance.end_date if instance else None)
        start_date = data.get('start_date', instance.start_date if instance else None)
        
        # Validación: end_date debe ser posterior a start_date
        if end_date and start_date:
            if end_date <= start_date:
                raise serializers.ValidationError({
                    "end_date": f"La fecha de fin ({end_date}) debe ser posterior a la fecha de inicio ({start_date})"
                })
        
        # Validación: Proyecto completed debe tener progress_pct = 100
        if status == "completed" and progress_pct != 100:
            raise serializers.ValidationError({
                "status": "Un proyecto completado debe tener progress_pct = 100",
                "progress_pct": "Para completar un proyecto, el progreso debe ser 100%"
            })
        
        # Validación: Proyecto planning debe tener progress_pct = 0
        if status == "planning" and progress_pct != 0:
            raise serializers.ValidationError({
                "progress_pct": "Un proyecto en planificación debe tener progress_pct = 0"
            })
        
        # Validación: Proyecto in_progress requiere project_manager
        if status == "in_progress" and not project_manager:
            raise serializers.ValidationError({
                "status": "Un proyecto en progreso requiere un project_manager asignado",
                "project_manager": "Debe asignar un project_manager para cambiar a 'in_progress'"
            })
        
        # Validación: Estados terminales no pueden cambiar
        if instance:
            estados_terminales = ["completed", "cancelled"]
            if instance.status in estados_terminales and status != instance.status:
                raise serializers.ValidationError({
                    "status": f"Un proyecto en estado '{instance.status}' no puede cambiar a otro estado. Los estados terminales son irreversibles."
                })
        
        # Validación: Proyecto cancelled no debe tener completed_at
        if status == "cancelled" and instance and instance.completed_at:
            data['completed_at'] = None
        
        return data


class ProyectoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados"""
    project_manager = serializers.StringRelatedField()

    class Meta:
        model = Proyecto
        fields = [
            "id",
            "code",
            "name",
            "status",
            "progress_pct",
            "project_manager",
            "start_date",
            "end_date",
            "created_at",
        ]
