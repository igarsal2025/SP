from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.companies.views import CompanyViewSet, SitecViewSet
from apps.accounts.views import AccessPolicyEvaluateView, AccessPolicyViewSet, MeView, UserContextView
from apps.accounts.views_auth import LoginView, LogoutView
from apps.accounts.views_mfa import MFASetupView, MFAVerifyView, MFADisableView, MFAStatusView
from apps.accounts.views_health import HealthCheckView, HealthCheckDetailedView
from apps.accounts.views_metrics import MetricsView
from apps.audit.views import AuditLogViewSet


router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"sitec", SitecViewSet, basename="sitec")
router.register(r"policies", AccessPolicyViewSet, basename="policy")
router.register(r"audit", AuditLogViewSet, basename="audit")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/login/", LoginView.as_view(), name="login"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
    path("api/auth/mfa/setup/", MFASetupView.as_view(), name="mfa-setup"),
    path("api/auth/mfa/verify/", MFAVerifyView.as_view(), name="mfa-verify"),
    path("api/auth/mfa/disable/", MFADisableView.as_view(), name="mfa-disable"),
    path("api/auth/mfa/status/", MFAStatusView.as_view(), name="mfa-status"),
    path("health/", HealthCheckView.as_view(), name="health"),
    path("health/detailed/", HealthCheckDetailedView.as_view(), name="health-detailed"),
    path("api/metrics/", MetricsView.as_view(), name="metrics"),
    path("api/users/me/", MeView.as_view(), name="me"),
    path("api/user/context/", UserContextView.as_view(), name="user-context"),
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
    path("api/transactions/", include("apps.transactions.urls")),
    path("", include("apps.frontend.urls")),
]
