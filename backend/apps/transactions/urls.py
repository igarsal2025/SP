from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import TransaccionViewSet, ClienteViewSet

app_name = "transactions"

router = DefaultRouter()
router.register(r"transacciones", TransaccionViewSet, basename="transaccion")
router.register(r"clientes", ClienteViewSet, basename="cliente")

urlpatterns = router.urls
