from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.companies.views import CompanyViewSet, SitecViewSet
from apps.accounts.views import AccessPolicyEvaluateView, AccessPolicyViewSet, MeView
from apps.audit.views import AuditLogViewSet


router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"sitec", SitecViewSet, basename="sitec")
router.register(r"policies", AccessPolicyViewSet, basename="policy")
router.register(r"audit", AuditLogViewSet, basename="audit")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/me/", MeView.as_view(), name="me"),
    path("api/policies/evaluate/", AccessPolicyEvaluateView.as_view(), name="policy-evaluate"),
    path("api/", include(router.urls)),
    path("api/wizard/", include("apps.frontend.api_urls")),
    path("api/ai/", include("apps.ai.urls")),
    path("api/rules/", include("apps.rules.urls")),
    path("api/sync/", include("apps.sync.urls")),
    path("api/reports/", include("apps.reports.urls")),
    path("api/projects/", include("apps.projects.urls")),
    path("api/documents/", include("apps.documents.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),
    path("api/roi/", include("apps.roi.urls")),
    path("", include("apps.frontend.urls")),
]
