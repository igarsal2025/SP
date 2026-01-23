from django.urls import path

from .views import RuleEvaluateView


urlpatterns = [
    path("evaluate/", RuleEvaluateView.as_view(), name="rules_evaluate"),
]
