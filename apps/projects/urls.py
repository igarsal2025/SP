from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import PresupuestoViewSet, ProyectoViewSet, RiesgoViewSet, TareaViewSet

app_name = "projects"

router = DefaultRouter()
router.register(r"proyectos", ProyectoViewSet, basename="proyecto")
router.register(r"tareas", TareaViewSet, basename="tarea")
router.register(r"riesgos", RiesgoViewSet, basename="riesgo")
router.register(r"presupuestos", PresupuestoViewSet, basename="presupuesto")

urlpatterns = router.urls
