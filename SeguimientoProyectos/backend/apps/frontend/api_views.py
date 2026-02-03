import json
import re
from pathlib import Path

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import log_audit_event
from apps.accounts.permissions import AccessPolicyPermission
from apps.accounts.models import AccessPolicy, UserProfile
from apps.accounts.services import build_context, matches_conditions

from .models import WizardDraft, WizardStepData
from apps.rules.services import evaluate_rules, get_active_ruleset
from .serializers import WizardDraftSerializer, WizardStepDataSerializer


class WizardSaveStepView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def post(self, request):
        step = int(request.data.get("step", 1))
        data = request.data.get("data", {})

        draft, _ = WizardDraft.objects.get_or_create(
            company=request.company,
            sitec=request.sitec,
            user=request.user,
            status="draft",
        )
        step_obj, _ = WizardStepData.objects.update_or_create(
            draft=draft,
            step=step,
            defaults={"data": data},
        )
        log_audit_event(request, "wizard_step_saved", step_obj)
        return Response(WizardStepDataSerializer(step_obj).data)


class WizardValidateView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def _get_policy_signature_requirements(self, request, profile, data=None):
        if not profile or not profile.company:
            return set()
        context = build_context(request, profile)
        if isinstance(data, dict):
            context.update(data)
        policies = AccessPolicy.objects.filter(
            company=profile.company,
            is_active=True,
            action__startswith="wizard.signature.require.",
        ).order_by("-priority")
        required = set()
        action_prefix = "wizard.signature.require."
        action_map = {
            "tech": "signature_tech",
            "tecnico": "signature_tech",
            "technician": "signature_tech",
            "supervisor": "signature_supervisor",
            "client": "signature_client",
            "cliente": "signature_client",
            "signature_tech": "signature_tech",
            "signature_supervisor": "signature_supervisor",
            "signature_client": "signature_client",
            "pm": "signature_supervisor",
            "admin": "signature_supervisor",
            "admin_empresa": "signature_supervisor",
        }
        for policy in policies:
            if not matches_conditions(policy.conditions, context):
                continue
            suffix = policy.action[len(action_prefix) :]
            field = action_map.get(suffix)
            if not field:
                continue
            if policy.effect == "allow":
                required.add(field)
            else:
                required.discard(field)
        return required

    def post(self, request):
        step = int(request.data.get("step", 1))
        data = request.data.get("data", {})

        critical = []
        warnings = []
        profile = UserProfile.objects.filter(user=request.user).first()
        role = profile.role if profile else None
        policy_required = self._get_policy_signature_requirements(request, profile, data)
        signature_requirements = set(policy_required)
        if role == "supervisor":
            signature_requirements.add("signature_supervisor")
        if role == "cliente":
            signature_requirements.add("signature_client")
        if data.get("signature_supervisor_required"):
            signature_requirements.add("signature_supervisor")

        if step == 1:
            required = ["project_name", "week_start", "site_address", "technician"]
            for key in required:
                if not data.get(key):
                    critical.append(f"{key}_required")
        elif step == 2:
            progress = data.get("progress_pct")
            if progress is None:
                critical.append("progress_pct_required")
            elif not (0 <= float(progress) <= 100):
                critical.append("progress_pct_invalid")
            if not data.get("schedule_status"):
                warnings.append("schedule_status_missing")
        elif step == 3:
            if not data.get("cabling_nodes_total"):
                critical.append("cabling_nodes_total_required")
            if data.get("cabling_nodes_ok") is None:
                warnings.append("cabling_nodes_ok_missing")
            if not data.get("cable_type"):
                warnings.append("cable_type_missing")
        elif step == 4:
            if data.get("racks_installed") is None:
                critical.append("racks_installed_required")
            if data.get("rack_order_ok") is False:
                warnings.append("rack_order_issue")
            if data.get("power_ok") is False:
                warnings.append("power_issue")
        elif step == 5:
            if data.get("security_devices") is None:
                critical.append("security_devices_required")
            elif int(data.get("security_devices", 0)) < 0:
                critical.append("security_devices_invalid")
            if data.get("cameras_online") is False:
                warnings.append("cameras_offline")
            if data.get("security_notes"):
                warnings.append("security_notes_present")
        elif step == 6:
            if data.get("special_systems_enabled") is True and not data.get(
                "special_systems_notes"
            ):
                critical.append("special_systems_notes_required")
            if data.get("special_systems_enabled") is True and not data.get(
                "special_systems_type"
            ):
                warnings.append("special_systems_type_missing")
        elif step == 7:
            if data.get("materials_count") is None:
                critical.append("materials_count_required")
            if not data.get("materials_list"):
                warnings.append("materials_list_missing")
            if data.get("missing_materials") is True and not data.get(
                "missing_materials_detail"
            ):
                warnings.append("missing_materials_detail_missing")
        elif step == 8:
            if data.get("tests_passed") is False:
                critical.append("tests_failed")
            if data.get("qa_signed") is False:
                warnings.append("qa_not_signed")
            if data.get("test_notes"):
                warnings.append("test_notes_present")
        elif step == 9:
            if not data.get("evidence_photos"):
                critical.append("evidence_photos_required")
            if not data.get("evidence_geo"):
                warnings.append("evidence_geo_missing")
            if data.get("evidence_ids"):
                warnings.append("evidence_ids_present")
        elif step == 10:
            if data.get("incidents") and not data.get("incidents_detail"):
                critical.append("incidents_detail_required")
            if data.get("incidents_severity") == "high" and not data.get("mitigation_plan"):
                critical.append("mitigation_plan_required")
            if data.get("incidents_count") and int(data.get("incidents_count", 0)) > 0:
                warnings.append("incidents_count_present")
        elif step == 11:
            if not data.get("signature_tech"):
                critical.append("signature_tech_required")
            if data.get("signature_supervisor_required") and not data.get("signature_supervisor"):
                critical.append("signature_supervisor_required")
            if role == "supervisor" and not data.get("signature_supervisor"):
                critical.append("signature_supervisor_required")
            if role == "cliente" and not data.get("signature_client"):
                critical.append("signature_client_required")
            if "signature_supervisor" in signature_requirements and not data.get("signature_supervisor"):
                critical.append("signature_supervisor_required")
            if "signature_client" in signature_requirements and not data.get("signature_client"):
                critical.append("signature_client_required")
            if "signature_tech" in signature_requirements and not data.get("signature_tech"):
                critical.append("signature_tech_required")
            if data.get("signature_method") == "webauthn" and not data.get("signature_date"):
                warnings.append("signature_date_missing")
        elif step == 12:
            if not data.get("final_review_ack"):
                critical.append("final_review_ack_required")
            if not data.get("report_summary"):
                warnings.append("report_summary_missing")
            if data.get("client_feedback"):
                warnings.append("client_feedback_present")

        ruleset = get_active_ruleset(request.company, request.sitec, "wizard")
        rule_results = evaluate_rules(ruleset, step, data)
        for item in rule_results:
            if item["severity"] == "critical":
                critical.append(item["code"])
            elif item["severity"] == "warning":
                warnings.append(item["code"])
        return Response(
            {
                "step": step,
                "critical": critical,
                "warnings": warnings,
                "allowed": len(critical) == 0,
                "rules_version": ruleset.version if ruleset else None,
                "rule_details": rule_results,
                "signature_requirements": sorted(signature_requirements),
            }
        )


class WizardSchemaView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def _resolve_schema_version(self, requested_version):
        schema_dir = Path(settings.BASE_DIR) / "static" / "frontend" / "schema"
        versions = []
        for path in schema_dir.glob("wizard_schema_v*.json"):
            match = re.search(r"wizard_schema_v(\d+)\.json$", path.name)
            if match:
                versions.append(int(match.group(1)))
        versions = sorted(set(versions))
        if not versions:
            return None, [], False
        if requested_version is None:
            return versions[-1], versions, False
        if requested_version in versions:
            return requested_version, versions, False
        lower = [v for v in versions if v <= requested_version]
        if lower:
            return lower[-1], versions, True
        return versions[-1], versions, True

    def get(self, request):
        raw_version = request.query_params.get("version")
        try:
            requested_version = int(raw_version) if raw_version else None
        except (TypeError, ValueError):
            requested_version = None
        resolved_version, available_versions, fallback_used = self._resolve_schema_version(
            requested_version
        )
        if not resolved_version:
            return Response({"error": "Schema no disponible"}, status=status.HTTP_404_NOT_FOUND)
        schema_path = (
            Path(settings.BASE_DIR)
            / "static"
            / "frontend"
            / "schema"
            / f"wizard_schema_v{resolved_version}.json"
        )
        if not schema_path.exists():
            return Response({"error": "Schema no disponible"}, status=status.HTTP_404_NOT_FOUND)
        with schema_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        data["schema_meta"] = {
            "requested_version": requested_version,
            "resolved_version": resolved_version,
            "fallback_used": fallback_used,
            "available_versions": available_versions,
        }
        log_audit_event(request, "wizard_schema_viewed", None)
        return Response(data)


class WizardSyncView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def _build_field_conflicts(self, server_data, client_data):
        ignore_fields = {"updatedAt", "schema_version"}
        conflicts = []
        server_data = server_data or {}
        client_data = client_data or {}
        for key in set(server_data.keys()) | set(client_data.keys()):
            if key in ignore_fields:
                continue
            if server_data.get(key) != client_data.get(key):
                conflicts.append(
                    {
                        "name": key,
                        "server": server_data.get(key),
                        "client": client_data.get(key),
                    }
                )
        return conflicts

    def post(self, request):
        incoming = request.data.get("steps", [])
        resolution = request.data.get("resolution", {})
        draft, _ = WizardDraft.objects.get_or_create(
            company=request.company,
            sitec=request.sitec,
            user=request.user,
            status="draft",
        )

        updated = []
        conflicts = []
        for step_payload in incoming:
            step = int(step_payload.get("step", 1))
            data = step_payload.get("data", {})
            existing = WizardStepData.objects.filter(draft=draft, step=step).first()
            choice = resolution.get(str(step)) or resolution.get(step)
            if isinstance(choice, dict) and choice.get("mode") == "merge" and existing:
                merged = {**(existing.data or {})}
                fields = choice.get("fields", {})
                for field, decision in fields.items():
                    if decision == "client":
                        merged[field] = data.get(field)
                    elif decision == "server":
                        merged[field] = (existing.data or {}).get(field)
                step_obj, _ = WizardStepData.objects.update_or_create(
                    draft=draft,
                    step=step,
                    defaults={"data": merged},
                )
                updated.append(WizardStepDataSerializer(step_obj).data)
                continue
            if choice == "server" and existing:
                updated.append(WizardStepDataSerializer(existing).data)
                continue
            if choice == "client":
                step_obj, _ = WizardStepData.objects.update_or_create(
                    draft=draft,
                    step=step,
                    defaults={"data": data},
                )
                updated.append(WizardStepDataSerializer(step_obj).data)
                continue

            if existing and existing.updated_at and data.get("updatedAt"):
                from django.utils.dateparse import parse_datetime
                from django.utils import timezone

                client_ts = data.get("updatedAt")
                client_dt = parse_datetime(client_ts) if isinstance(client_ts, str) else client_ts
                if client_dt and timezone.is_naive(client_dt):
                    client_dt = timezone.make_aware(client_dt)
                if client_dt and client_dt < existing.updated_at:
                    conflicts.append(
                        {
                            "step": step,
                            "fields": self._build_field_conflicts(existing.data, data),
                            "server_updated_at": existing.updated_at.isoformat(),
                            "client_updated_at": client_ts,
                        }
                    )
                    continue

            step_obj, _ = WizardStepData.objects.update_or_create(
                draft=draft,
                step=step,
                defaults={"data": data},
            )
            updated.append(WizardStepDataSerializer(step_obj).data)

        log_audit_event(request, "wizard_sync", draft)
        return Response(
            {
                "draft": WizardDraftSerializer(draft).data,
                "updated_steps": updated,
                "conflicts": conflicts,
            }
        )


class WizardAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def post(self, request):
        step_times = request.data.get("step_times", [])
        completed_steps = request.data.get("completed_steps", [])
        total_time = request.data.get("total_time", 0)

        # Guardar analytics (puede almacenarse en BD o solo en logs)
        log_audit_event(
            request,
            "wizard_analytics",
            None,
            extra_data={
                "step_times": step_times,
                "completed_steps": completed_steps,
                "total_time": total_time,
            },
        )

        return Response({"status": "ok"})


class VerifyPasswordView(APIView):
    permission_classes = [IsAuthenticated, AccessPolicyPermission]

    def post(self, request):
        password = request.data.get("password")
        if not password:
            return Response(
                {"error": "Password required"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=request.user.username, password=password)
        if user and user == request.user:
            log_audit_event(request, "reauthentication_success", request.user)
            return Response({"verified": True})
        else:
            log_audit_event(request, "reauthentication_failed", request.user)
            return Response(
                {"verified": False, "error": "Invalid password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


@method_decorator(csrf_exempt, name="dispatch")
class PerformanceMetricsView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        def _to_float(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return None

        fcp = _to_float(request.data.get("fcp"))
        tti = _to_float(request.data.get("tti"))
        lcp = _to_float(request.data.get("lcp"))
        cls = _to_float(request.data.get("cls"))
        ttfb = _to_float(request.data.get("ttfb"))
        js_size = _to_float(request.data.get("js_size"))
        resource_count = _to_float(request.data.get("resource_count"))
        load_time = _to_float(request.data.get("load_time"))
        url = request.data.get("url")
        timestamp = request.data.get("timestamp")
        connection = request.data.get("connection")

        # Log de métricas de performance (puede almacenarse en BD si se desea)
        log_audit_event(
            request,
            "performance_metrics",
            None,
            extra_data={
                "fcp": fcp,
                "tti": tti,
                "lcp": lcp,
                "cls": cls,
                "ttfb": ttfb,
                "js_size": js_size,
                "resource_count": resource_count,
                "load_time": load_time,
                "url": url,
                "connection": connection,
                "timestamp": timestamp,
            },
        )

        # Verificar si excede límites
        warnings = []
        if fcp and fcp > 1000:
            warnings.append(f"FCP ({fcp}ms) exceeds 1000ms limit")
        if tti and tti > 2500:
            warnings.append(f"TTI ({tti}ms) exceeds 2500ms limit")
        if lcp and lcp > 2500:
            warnings.append(f"LCP ({lcp}ms) exceeds 2500ms limit")
        if cls and cls > 0.1:
            warnings.append(f"CLS ({cls}) exceeds 0.1 limit")
        if ttfb and ttfb > 800:
            warnings.append(f"TTFB ({ttfb}ms) exceeds 800ms limit")
        if js_size and js_size > 100 * 1024:
            warnings.append(f"JS size ({js_size / 1024:.2f}KB) exceeds 100KB limit")

        return Response({"status": "ok", "warnings": warnings})
