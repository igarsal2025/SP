from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import DocumentVerifyView, DocumentViewSet

app_name = "documents"

router = DefaultRouter()
router.register(r"documents", DocumentViewSet, basename="document")

urlpatterns = [
    path("verify/<uuid:token>/", DocumentVerifyView.as_view(), name="document-verify"),
]

urlpatterns += router.urls
