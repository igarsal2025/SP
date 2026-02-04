from rest_framework import serializers

from .models import WizardDraft, WizardStepData


class WizardStepDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = WizardStepData
        fields = ["id", "draft", "step", "data", "updated_at"]


class WizardDraftSerializer(serializers.ModelSerializer):
    steps = WizardStepDataSerializer(many=True, read_only=True)

    class Meta:
        model = WizardDraft
        fields = ["id", "company", "sitec", "user", "status", "steps", "created_at", "updated_at"]
