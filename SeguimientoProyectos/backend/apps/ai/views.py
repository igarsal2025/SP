import time

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import AccessPolicyPermission
from apps.audit.services import log_audit_event

from .models import AiAsset, AiSuggestion
from .providers import HeavyProvider, LightModelProvider, RuleProvider
from .tasks import run_heavy_suggestion
from .serializers import AiAssetSerializer, AiSuggestionSerializer


CONTRACT = {
    "request": {
        "step": "int",
        "data": "object",
        "mode": "quick|heavy",
    },
    "response": {
        "status": "success|queued|fallback|error",
        "fallback": "bool",
        "model": {"name": "string", "version": "string"},
        "latency_ms": "int",
        "suggestions": [
            {
                "field": "string",
                "value": "string|number|bool",
                "confidence": "float",
                "reason": "string",
                "tier": "rule|light|heavy",
            }
        ],
    },
}


rule_provider = RuleProvider()
light_provider = LightModelProvider()


def _avg_confidence(suggestions):
    if not suggestions:
        return None
    return sum(item.get("confidence", 0) for item in suggestions) / len(suggestions)


class AiContractView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get(self, request):
        return Response(CONTRACT)


class AiSuggestView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def post(self, request):
        step = int(request.data.get("step", 1))
        data = request.data.get("data", {})
        mode = request.data.get("mode", "quick")

        start = time.perf_counter()
        suggestions = rule_provider.suggest(step, data)
        light_suggestions = light_provider.suggest(step, data)
        existing_fields = {item.get("field") for item in suggestions}
        for item in light_suggestions:
            if item.get("field") not in existing_fields:
                suggestions.append(item)
        latency_ms = int((time.perf_counter() - start) * 1000)

        status_value = "success"
        fallback = False
        if mode == "heavy":
            status_value = "queued"
            fallback = True

        model_name = light_provider.name if light_suggestions else rule_provider.name
        model_version = light_provider.version if light_suggestions else rule_provider.version

        output = {
            "status": status_value,
            "fallback": fallback,
            "model": {"name": model_name, "version": model_version},
            "latency_ms": latency_ms,
            "suggestions": suggestions,
            "suggestion_id": None,
        }

        record = AiSuggestion.objects.create(
            company=request.company,
            sitec=request.sitec,
            user=request.user,
            step=step,
            mode=mode,
            model_name=model_name,
            model_version=model_version,
            input_snapshot=data,
            output=output,
            confidence=_avg_confidence(suggestions),
            latency_ms=latency_ms,
            status="fallback" if fallback else "success",
        )

        if mode == "heavy":
            output["suggestion_id"] = str(record.id)
            run_heavy_suggestion.delay(str(record.id))

        log_audit_event(request, "ai_suggest", record, extra_data={"mode": mode})
        return Response(output, status=status.HTTP_200_OK)


class AiSuggestionStatusView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get(self, request, suggestion_id):
        suggestion = AiSuggestion.objects.filter(
            id=suggestion_id, company=request.company, sitec=request.sitec
        ).first()
        if not suggestion:
            return Response({"error": "Sugerencia no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {
                "id": str(suggestion.id),
                "status": suggestion.status,
                "output": suggestion.output,
                "latency_ms": suggestion.latency_ms,
            }
        )


class AiAssetCreateView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def post(self, request):
        serializer = AiAssetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        asset = serializer.save(
            company=request.company,
            sitec=request.sitec,
            user=request.user,
        )
        log_audit_event(request, "ai_asset_created", asset)
        return Response(AiAssetSerializer(asset).data, status=status.HTTP_201_CREATED)
