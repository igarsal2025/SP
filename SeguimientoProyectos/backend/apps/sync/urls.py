from django.urls import path

from .views import SyncSessionView, SyncView

app_name = "sync"

urlpatterns = [
    path("", SyncView.as_view(), name="sync"),
    path("sessions/", SyncSessionView.as_view(), name="sync_sessions"),
    path("sessions/<uuid:session_id>/", SyncSessionView.as_view(), name="sync_session_detail"),
]
