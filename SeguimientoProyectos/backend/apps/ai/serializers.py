from rest_framework import serializers

from .models import AiAsset, AiSuggestion


class AiSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiSuggestion
        fields = [
            "id",
            "company",
            "sitec",
            "user",
            "step",
            "mode",
            "model_name",
            "model_version",
            "input_snapshot",
            "output",
            "confidence",
            "latency_ms",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "company", "sitec", "user", "created_at"]


class AiAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiAsset
        fields = [
            "id",
            "company",
            "sitec",
            "user",
            "suggestion",
            "asset_type",
            "hash",
            "embedding",
            "metadata",
            "created_at",
        ]
        read_only_fields = ["id", "company", "sitec", "user", "created_at"]
