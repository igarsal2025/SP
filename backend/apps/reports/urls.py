from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import EvidenciaViewSet, IncidenteViewSet, ReporteSemanalViewSet

app_name = "reports"

router = DefaultRouter()
router.register(r"reportes", ReporteSemanalViewSet, basename="reporte")
router.register(r"evidencias", EvidenciaViewSet, basename="evidencia")
router.register(r"incidentes", IncidenteViewSet, basename="incidente")

urlpatterns = router.urls
