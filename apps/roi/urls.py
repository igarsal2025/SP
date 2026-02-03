from django.urls import path

from .views import RoiExportView, RoiHistoryView, RoiSnapshotView
from .views_advanced import RoiAnalysisView, RoiGoalsView, RoiTrendsView

app_name = "roi"

urlpatterns = [
    path("", RoiSnapshotView.as_view(), name="roi"),
    path("history/", RoiHistoryView.as_view(), name="roi-history"),
    path("export/", RoiExportView.as_view(), name="roi-export"),
    # Endpoints avanzados
    path("trends/", RoiTrendsView.as_view(), name="roi-trends"),
    path("goals/", RoiGoalsView.as_view(), name="roi-goals"),
    path("analysis/", RoiAnalysisView.as_view(), name="roi-analysis"),
]
