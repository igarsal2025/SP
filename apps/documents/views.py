from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Q

from apps.accounts.mixins import CompanySitecQuerysetMixin
from apps.accounts.permissions import AccessPolicyPermission
from apps.accounts.models import UserProfile
from apps.audit.services import log_audit_event
from apps.reports.models import ReporteSemanal

from .models import Document
from .serializers import DocumentSerializer
from .tasks import generate_report_document


def _can_access_document(request, document):
    if document.company_id != request.company.id or document.sitec_id != request.sitec.id:
        return False
    profile = UserProfile.objects.select_related("company").filter(user=request.user).first()
    if profile and profile.role == "admin_empresa":
        return True
    report = document.report
    if report and report.technician_id == request.user.id:
        return True
    if report and report.supervisor_id == request.user.id:
        return True
    if report and report.project and report.project.project_manager_id == request.user.id:
        return True
    return False


class DocumentViewSet(CompanySitecQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.select_related(
        "report",
        "report__project",
        "report__technician",
        "report__supervisor",
        "company",
        "sitec",
    ).all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        profile = UserProfile.objects.select_related("company").filter(user=self.request.user).first()
        if not profile or profile.role != "admin_empresa":
            queryset = queryset.filter(
                Q(report__technician=self.request.user)
                | Q(report__supervisor=self.request.user)
                | Q(report__project__project_manager=self.request.user)
            )
        report_id = self.request.query_params.get("report")
        if report_id:
            queryset = queryset.filter(report_id=report_id)
        return queryset

    @action(detail=False, methods=["post"])
    def report(self, request):
        report_id = request.data.get("report_id")
        if not report_id:
            return Response({"error": "report_id requerido"}, status=status.HTTP_400_BAD_REQUEST)

        report = ReporteSemanal.objects.filter(
            id=report_id, company=request.company, sitec=request.sitec
        ).first()
        if not report:
            return Response({"error": "Reporte no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        latest = (
            Document.objects.filter(report=report)
            .order_by("-version")
            .values_list("version", flat=True)
            .first()
            or 0
        )
        document = Document.objects.create(
            company=request.company,
            sitec=request.sitec,
            report=report,
            created_by=request.user,
            version=latest + 1,
            status="pending",
            issued_at=None,
        )
        log_audit_event(request, "document_generation_requested", document)

        generate_report_document.delay(str(document.id))
        return Response(DocumentSerializer(document).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        document = self.get_object()
        if not _can_access_document(request, document):
            return Response({"error": "Acceso no autorizado"}, status=status.HTTP_403_FORBIDDEN)
        if document.status != "ready" or not document.file_path:
            return Response({"error": "Documento no disponible"}, status=status.HTTP_400_BAD_REQUEST)
        storage_root = (Path(settings.BASE_DIR) / "storage" / "documents").resolve()
        file_path = Path(document.file_path).resolve()
        if not str(file_path).startswith(str(storage_root)):
            return Response({"error": "Ruta de documento no valida"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            response = FileResponse(open(file_path, "rb"), content_type=document.mime_type)
        except FileNotFoundError as exc:
            raise Http404("Archivo no encontrado") from exc
        response["Content-Disposition"] = f'attachment; filename="{document.file_name}"'
        return response


class DocumentVerifyView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def get(self, request, token):
        document = Document.objects.filter(qr_token=token).first()
        if not document:
            return Response({"error": "Token no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        if not _can_access_document(request, document):
            return Response({"error": "Acceso no autorizado"}, status=status.HTTP_403_FORBIDDEN)
        payload = {
            "document_id": str(document.id),
            "report_id": str(document.report_id),
            "checksum_sha256": document.checksum_sha256,
            "issued_at": document.issued_at,
            "status": document.status,
            "nom151_stamp": document.nom151_stamp,
            "verified_at": timezone.now(),
        }
        return Response(payload)
