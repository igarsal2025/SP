from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import log_audit_event

from .models import AccessPolicy, UserProfile
from .services import action_from_request, evaluate_access_policy
from .permissions import AccessPolicyPermission
from .serializers import AccessPolicySerializer, UserProfileSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={"company_id": None, "role": "cliente"},
        )
        return Response(UserProfileSerializer(profile).data)

    def patch(self, request):
        profile, _ = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={"company_id": None, "role": "cliente"},
        )
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        log_audit_event(request, "user_profile_updated", profile)
        return Response(serializer.data)


class AccessPolicyViewSet(viewsets.ModelViewSet):
    queryset = AccessPolicy.objects.select_related("company").all().order_by("-priority")
    serializer_class = AccessPolicySerializer
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def perform_create(self, serializer):
        policy = serializer.save()
        log_audit_event(self.request, "policy_created", policy)

    def perform_update(self, serializer):
        policy = serializer.save()
        log_audit_event(self.request, "policy_updated", policy)


class AccessPolicyEvaluateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        action_name = request.data.get("action")
        if not action_name:
            action_name = action_from_request(request, self)
        decision = evaluate_access_policy(request, action_name)
        return Response(
            {
                "action": action_name,
                "allowed": decision.allowed,
                "policy_id": decision.policy_id,
                "policy_action": decision.policy_action,
                "policy_effect": decision.policy_effect,
            }
        )
