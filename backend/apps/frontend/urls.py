from django.urls import path

from .views import (
    WizardStepView,
    LoginView,
    OfflineView,
    DashboardView,
    ProjectsView,
    ReportsView,
    DocumentsView,
    ApprovalsView,
    ProjectDetailView,
    ProjectEditView,
    ProjectCreateView,
    ReportDetailView,
    MFAView,
    manifest_view,
    service_worker_view,
)


urlpatterns = [
    path("login/", LoginView.as_view(), name="login_page"),
    path("", WizardStepView.as_view(), name="wizard_home"),
    path("wizard/<int:step>/", WizardStepView.as_view(), name="wizard_step"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("projects/", ProjectsView.as_view(), name="projects"),
    path("projects/create/", ProjectCreateView.as_view(), name="project_create"),
    path("projects/<uuid:project_id>/", ProjectDetailView.as_view(), name="project_detail"),
    path("projects/<uuid:project_id>/edit/", ProjectEditView.as_view(), name="project_edit"),
    path("reports/", ReportsView.as_view(), name="reports"),
    path("reports/<uuid:report_id>/", ReportDetailView.as_view(), name="report_detail"),
    path("reports/approvals/", ApprovalsView.as_view(), name="approvals"),
    path("documents/", DocumentsView.as_view(), name="documents"),
    path("settings/mfa/", MFAView.as_view(), name="mfa_settings"),
    path("offline.html", OfflineView.as_view(), name="offline"),
    path("manifest.json", manifest_view, name="manifest"),
    path("sw.js", service_worker_view, name="service_worker"),
]
