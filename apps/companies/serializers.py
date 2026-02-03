from rest_framework import serializers

from .models import Company, Sitec


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "rfc",
            "tax_regime",
            "timezone",
            "locale",
            "plan",
            "status",
            "created_at",
            "updated_at",
        ]


class SitecSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sitec
        fields = [
            "id",
            "schema_name",
            "company",
            "status",
            "activated_at",
            "created_at",
            "updated_at",
        ]
