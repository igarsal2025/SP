import json
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView


class WizardStepView(TemplateView):
    template_name = "frontend/wizard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        step = self.kwargs.get("step", 1)
        context["step"] = step
        context["total_steps"] = 12
        context["company"] = getattr(self.request, "company", None)
        context["sitec"] = getattr(self.request, "sitec", None)
        context["project_id"] = self.request.GET.get("project") or ""
        context["report_id"] = self.request.GET.get("report") or ""
        return context


class OfflineView(TemplateView):
    template_name = "frontend/offline.html"


class DashboardView(TemplateView):
    template_name = "frontend/dashboard.html"


def manifest_view(request):
    manifest_path = Path(settings.BASE_DIR.parent) / "backend" / "static" / "frontend" / "pwa" / "manifest.json"
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
        return JsonResponse(manifest_data, content_type="application/manifest+json")
    except FileNotFoundError:
        return JsonResponse({"error": "Manifest not found"}, status=404)


def service_worker_view(request):
    sw_path = Path(settings.BASE_DIR.parent) / "backend" / "static" / "frontend" / "pwa" / "sw.js"
    try:
        with open(sw_path, "r", encoding="utf-8") as f:
            sw_content = f.read()
        response = HttpResponse(sw_content, content_type="application/javascript")
        response["Service-Worker-Allowed"] = "/"
        return response
    except FileNotFoundError:
        return HttpResponse("Service Worker not found", status=404, content_type="text/plain")
