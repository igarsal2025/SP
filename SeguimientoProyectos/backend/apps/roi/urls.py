from django.urls import path

from .views import RoiExportView, RoiHistoryView, RoiSnapshotView

app_name = "roi"

urlpatterns = [
    path("", RoiSnapshotView.as_view(), name="roi"),
    path("history/", RoiHistoryView.as_view(), name="roi-history"),
    path("export/", RoiExportView.as_view(), name="roi-export"),
]
