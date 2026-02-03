from django.urls import path

from .views import (
    WizardStepView,
    OfflineView,
    DashboardView,
    manifest_view,
    service_worker_view,
)


urlpatterns = [
    path("", WizardStepView.as_view(), name="wizard_home"),
    path("wizard/<int:step>/", WizardStepView.as_view(), name="wizard_step"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("offline.html", OfflineView.as_view(), name="offline"),
    path("manifest.json", manifest_view, name="manifest"),
    path("sw.js", service_worker_view, name="service_worker"),
]
