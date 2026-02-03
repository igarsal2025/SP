from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import AccessPolicyPermission

from .services import evaluate_rules, get_active_ruleset


class RuleEvaluateView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def post(self, request):
        step = int(request.data.get("step", 1))
        data = request.data.get("data", {})
        ruleset = get_active_ruleset(request.company, request.sitec, "wizard")
        results = evaluate_rules(ruleset, step, data)
        return Response(
            {
                "rules_version": ruleset.version if ruleset else None,
                "results": results,
            },
            status=status.HTTP_200_OK,
        )
