from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = [
            "id",
            "company",
            "actor",
            "action",
            "entity_type",
            "entity_id",
            "before",
            "after",
            "ip_address",
            "user_agent",
            "created_at",
        ]
