from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.audit.services import log_audit_event

from .models import Company, Sitec
from .serializers import CompanySerializer, SitecSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all().order_by("name")
    serializer_class = CompanySerializer

    def perform_create(self, serializer):
        company = serializer.save()
        log_audit_event(self.request, "company_created", company)

    def perform_update(self, serializer):
        company = serializer.save()
        log_audit_event(self.request, "company_updated", company)


class SitecViewSet(viewsets.ModelViewSet):
    queryset = Sitec.objects.select_related("company").all().order_by("-created_at")
    serializer_class = SitecSerializer

    def perform_create(self, serializer):
        sitec = serializer.save()
        log_audit_event(self.request, "sitec_created", sitec)

    def perform_update(self, serializer):
        sitec = serializer.save()
        log_audit_event(self.request, "sitec_updated", sitec)

    @action(detail=True, methods=["patch"], url_path="status")
    def update_status(self, request, pk=None):
        sitec = self.get_object()
        new_status = request.data.get("status")
        if new_status not in ["active", "suspended"]:
            return Response(
                {"detail": "Estado invalido."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        sitec.status = new_status
        if new_status == "active" and sitec.activated_at is None:
            sitec.activated_at = timezone.now()
        sitec.save(update_fields=["status", "activated_at", "updated_at"])
        log_audit_event(request, "sitec_status_updated", sitec)
        return Response(SitecSerializer(sitec).data)
