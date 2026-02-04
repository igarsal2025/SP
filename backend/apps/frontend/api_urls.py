from django.urls import path

from .api_views import (
    PerformanceMetricsView,
    VerifyPasswordView,
    WizardAnalyticsView,
    WizardSaveStepView,
  WizardSchemaView,
    WizardSyncView,
    WizardValidateView,
)


urlpatterns = [
    path("steps/save/", WizardSaveStepView.as_view(), name="wizard_save_step"),
  path("schema/", WizardSchemaView.as_view(), name="wizard_schema"),
    path("validate/", WizardValidateView.as_view(), name="wizard_validate"),
    path("sync/", WizardSyncView.as_view(), name="wizard_sync"),
    path("analytics/", WizardAnalyticsView.as_view(), name="wizard_analytics"),
    path("verify-password/", VerifyPasswordView.as_view(), name="wizard_verify_password"),
    path("performance/metrics/", PerformanceMetricsView.as_view(), name="performance_metrics"),
]
