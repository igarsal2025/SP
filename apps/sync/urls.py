from django.urls import path

from .views import SyncSessionView, SyncView
from .views_conflicts import ConflictDiffView, ConflictResolutionView

app_name = "sync"

urlpatterns = [
    path("", SyncView.as_view(), name="sync"),
    path("sessions/", SyncSessionView.as_view(), name="sync_sessions"),
    path("sessions/<uuid:session_id>/", SyncSessionView.as_view(), name="sync_session_detail"),
    # Endpoints de conflictos avanzados
    path(
        "sessions/<uuid:session_id>/conflicts/<uuid:item_id>/diff/",
        ConflictDiffView.as_view(),
        name="sync-conflict-diff"
    ),
    path(
        "sessions/<uuid:session_id>/conflicts/<uuid:item_id>/resolve/",
        ConflictResolutionView.as_view(),
        name="sync-conflict-resolve"
    ),
]
