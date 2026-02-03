from django.urls import path

from .views import (
    DashboardAggregateHistoryView,
    DashboardKpiView,
    DashboardSnapshotHistoryView,
    DashboardTrendsView,
)

app_name = "dashboard"

urlpatterns = [
    path("", DashboardKpiView.as_view(), name="kpis"),
    path("history/", DashboardSnapshotHistoryView.as_view(), name="history"),
    path("aggregates/", DashboardAggregateHistoryView.as_view(), name="aggregates"),
    path("trends/", DashboardTrendsView.as_view(), name="trends"),
]
