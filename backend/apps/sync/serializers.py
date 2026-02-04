from rest_framework import serializers

from .models import SyncItem, SyncSession


class SyncItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncItem
        fields = [
            "id",
            "entity_type",
            "entity_id",
            "status",
            "client_timestamp",
            "server_timestamp",
            "data",
            "error_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SyncSessionSerializer(serializers.ModelSerializer):
    items = SyncItemSerializer(many=True, read_only=True)

    class Meta:
        model = SyncSession
        fields = [
            "id",
            "company",
            "sitec",
            "user",
            "status",
            "items_synced",
            "items_failed",
            "conflicts_detected",
            "started_at",
            "completed_at",
            "error_message",
            "metadata",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "items_synced",
            "items_failed",
            "conflicts_detected",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        ]


class SyncRequestSerializer(serializers.Serializer):
    """Serializer para requests de sincronización"""
    items = serializers.ListField(
        child=serializers.DictField(),
        help_text="Lista de items a sincronizar",
    )
    resolution = serializers.DictField(
        required=False,
        help_text="Resolución de conflictos: {entity_id: 'client'|'server'|{'mode':'merge','fields':{campo:'client'|'server'}}}",
    )
    session_id = serializers.UUIDField(
        required=False,
        help_text="ID de sesión existente para continuar sync",
    )


class SyncResponseSerializer(serializers.Serializer):
    """Serializer para respuestas de sincronización"""
    session = SyncSessionSerializer()
    synced_items = SyncItemSerializer(many=True)
    conflicts = serializers.ListField(
        child=serializers.CharField(),
        help_text="IDs de items con conflictos",
    )
