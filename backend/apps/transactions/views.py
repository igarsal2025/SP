import uuid
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.mixins import CompanySitecQuerysetMixin
from apps.accounts.permissions import AccessPolicyPermission
from apps.audit.services import log_audit_event

from .models import Transaccion, Cliente
from .serializers import TransaccionSerializer, TransaccionCreateSerializer, ClienteSerializer


class ClienteViewSet(CompanySitecQuerysetMixin, viewsets.ModelViewSet):
    """ViewSet para clientes"""
    queryset = Cliente.objects.select_related('company', 'sitec').all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated, AccessPolicyPermission]
    
    def perform_create(self, serializer):
        """Asignar company y sitec automáticamente"""
        cliente = serializer.save(
            company=self.request.company,
            sitec=self.request.sitec
        )
        log_audit_event(
            request=self.request,
            action='create',
            instance=cliente
        )


class TransaccionViewSet(CompanySitecQuerysetMixin, viewsets.ModelViewSet):
    """ViewSet para transacciones"""
    queryset = Transaccion.objects.select_related(
        'company', 'sitec', 'id_cliente'
    ).all()
    permission_classes = [IsAuthenticated, AccessPolicyPermission]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TransaccionCreateSerializer
        return TransaccionSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros adicionales
        estado_filter = self.request.query_params.get('estado')
        if estado_filter:
            queryset = queryset.filter(estado=estado_filter)
        
        moneda_filter = self.request.query_params.get('moneda')
        if moneda_filter:
            queryset = queryset.filter(moneda=moneda_filter)
        
        cliente_filter = self.request.query_params.get('id_cliente')
        if cliente_filter:
            try:
                cliente_uuid = uuid.UUID(str(cliente_filter))
                queryset = queryset.filter(id_cliente_id=cliente_uuid)
            except (ValueError, TypeError):
                pass  # Ignorar valores no UUID para evitar 500 en filtros mal formados
        
        fecha_desde = self.request.query_params.get('fecha__gte')
        if fecha_desde:
            try:
                from django.utils.dateparse import parse_datetime
                dt = parse_datetime(fecha_desde)
                if dt is not None:
                    queryset = queryset.filter(fecha__gte=dt)
            except (ValueError, TypeError):
                pass
        
        fecha_hasta = self.request.query_params.get('fecha__lte')
        if fecha_hasta:
            try:
                from django.utils.dateparse import parse_datetime
                dt = parse_datetime(fecha_hasta)
                if dt is not None:
                    queryset = queryset.filter(fecha__lte=dt)
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    def perform_create(self, serializer):
        """Asignar company y sitec automáticamente y validar cliente"""
        # Verificar autenticación explícitamente
        if not self.request.user or not self.request.user.is_authenticated:
            raise serializers.ValidationError({
                'non_field_errors': ['Autenticación requerida']
            })
        
        # Verificar permisos mediante AccessPolicyPermission
        from apps.accounts.permissions import AccessPolicyPermission
        from apps.accounts.services import action_from_request
        permission = AccessPolicyPermission()
        action_name = action_from_request(self.request, self)
        if not permission.has_permission(self.request, self):
            raise serializers.ValidationError({
                'non_field_errors': ['No tiene permisos para realizar esta acción']
            })
        
        # Verificar que el cliente pertenece a la misma empresa
        cliente_id = serializer.validated_data.get('id_cliente')
        if cliente_id:
            cliente = Cliente.objects.get(id=cliente_id.id)
            if cliente.company != self.request.company:
                raise serializers.ValidationError({
                    'id_cliente': 'El cliente no pertenece a su empresa'
                })
        
        transaccion = serializer.save(
            company=self.request.company,
            sitec=self.request.sitec
        )
        
        log_audit_event(
            request=self.request,
            action='create',
            instance=transaccion
        )
    
    def perform_update(self, serializer):
        """Registrar cambios en audit log"""
        # Verificar autenticación explícitamente
        if not self.request.user or not self.request.user.is_authenticated:
            raise serializers.ValidationError({
                'non_field_errors': ['Autenticación requerida']
            })
        
        # Verificar permisos mediante AccessPolicyPermission
        from apps.accounts.permissions import AccessPolicyPermission
        from apps.accounts.services import action_from_request
        permission = AccessPolicyPermission()
        action_name = action_from_request(self.request, self)
        if not permission.has_permission(self.request, self):
            raise serializers.ValidationError({
                'non_field_errors': ['No tiene permisos para realizar esta acción']
            })
        
        instance = serializer.instance
        before = {
            'id_transaccion': str(instance.id_transaccion),
            'monto': str(instance.monto),
            'moneda': instance.moneda,
            'estado': instance.estado,
        }
        
        transaccion = serializer.save()
        
        log_audit_event(
            request=self.request,
            action='update',
            instance=transaccion,
            before=before
        )
    
    def perform_destroy(self, instance):
        """Registrar eliminación en audit log"""
        # Verificar autenticación explícitamente
        if not self.request.user or not self.request.user.is_authenticated:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Autenticación requerida')
        
        # Verificar permisos mediante AccessPolicyPermission
        from apps.accounts.permissions import AccessPolicyPermission
        from apps.accounts.services import action_from_request
        permission = AccessPolicyPermission()
        action_name = action_from_request(self.request, self)
        if not permission.has_permission(self.request, self):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('No tiene permisos para realizar esta acción')
        
        before = {
            'id_transaccion': str(instance.id_transaccion),
            'monto': str(instance.monto),
            'moneda': instance.moneda,
            'estado': instance.estado,
        }
        log_audit_event(
            request=self.request,
            action='delete',
            instance=instance,
            before=before
        )
        instance.delete()
