import json
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView


class WizardStepView(TemplateView):
    template_name = "frontend/wizard.html"

    def get_template_names(self):
        user_context = getattr(self.request, "user_context", None) or {}
        ui_config = user_context.get("ui_config", {})
        wizard_mode = ui_config.get("wizard_mode", "full")
        
        if wizard_mode == "readonly":
            return ["frontend/wizard/wizard_readonly.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        step = self.kwargs.get("step", 1)
        context["step"] = step
        context["total_steps"] = 12
        context["company"] = getattr(self.request, "company", None)
        context["sitec"] = getattr(self.request, "sitec", None)
        context["project_id"] = self.request.GET.get("project") or ""
        context["report_id"] = self.request.GET.get("report") or ""
        context["user_context"] = getattr(self.request, "user_context", None)
        return context


class OfflineView(TemplateView):
    template_name = "frontend/offline.html"


class DashboardView(TemplateView):
    template_name = "frontend/dashboard.html"

    def get_template_names(self):
        user_context = getattr(self.request, "user_context", None) or {}
        role = (user_context.get("profile") or {}).get("role")
        if role == "admin_empresa":
            return ["frontend/dashboard/admin.html"]
        if role == "pm":
            return ["frontend/dashboard/pm.html"]
        if role == "supervisor":
            return ["frontend/dashboard/supervisor.html"]
        if role == "tecnico":
            return ["frontend/dashboard/tecnico.html"]
        if role == "cliente":
            return ["frontend/dashboard/cliente.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_context"] = getattr(self.request, "user_context", None)
        return context


class ProjectsView(TemplateView):
    template_name = "frontend/projects/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_context"] = getattr(self.request, "user_context", None)
        return context


class ReportsView(TemplateView):
    template_name = "frontend/reports/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_context"] = getattr(self.request, "user_context", None)
        return context


class ApprovalsView(TemplateView):
    template_name = "frontend/reports/approvals.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_context"] = getattr(self.request, "user_context", None)
        return context


class DocumentsView(TemplateView):
    template_name = "frontend/documents/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_context"] = getattr(self.request, "user_context", None)
        return context


class ProjectDetailView(TemplateView):
    template_name = "frontend/projects/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_id"] = self.kwargs.get("project_id")
        context["user_context"] = getattr(self.request, "user_context", None)
        return context


class ProjectEditView(TemplateView):
    template_name = "frontend/projects/edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_id"] = self.kwargs.get("project_id")
        context["user_context"] = getattr(self.request, "user_context", None)
        return context


class ProjectCreateView(TemplateView):
    template_name = "frontend/projects/create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_context"] = getattr(self.request, "user_context", None)
        return context


class ReportDetailView(TemplateView):
    template_name = "frontend/reports/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["report_id"] = self.kwargs.get("report_id")
        context["user_context"] = getattr(self.request, "user_context", None)
        return context


class MFAView(TemplateView):
    template_name = "frontend/settings/mfa.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_context"] = getattr(self.request, "user_context", None)
        return context


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
