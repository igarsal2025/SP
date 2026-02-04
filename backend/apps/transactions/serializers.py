from rest_framework import serializers
from .models import Transaccion, Cliente


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = [
            'id',
            'nombre',
            'email',
            'activo',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TransaccionSerializer(serializers.ModelSerializer):
    id_cliente_nombre = serializers.CharField(source='id_cliente.nombre', read_only=True)
    
    class Meta:
        model = Transaccion
        fields = [
            'id_transaccion',
            'id_cliente',
            'id_cliente_nombre',
            'monto',
            'moneda',
            'fecha',
            'estado',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id_transaccion',
            'created_at',
            'updated_at',
        ]


class TransaccionCreateSerializer(serializers.ModelSerializer):
    """Serializer para creación que no permite modificar campos protegidos"""
    
    class Meta:
        model = Transaccion
        fields = [
            'id_cliente',
            'monto',
            'moneda',
            'fecha',
            'estado',
        ]
        extra_kwargs = {
            'moneda': {'required': False},
            'fecha': {'required': False},
            'estado': {'required': False},
        }
