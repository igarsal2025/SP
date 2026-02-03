import json
from pathlib import Path

from django.conf import settings


class BaseAiProvider:
    name = "base"
    version = "v1"

    def suggest(self, step, data):
        raise NotImplementedError


class LightModelProvider(BaseAiProvider):
    name = "light_model"
    version = "v1"

    _config = None

    def _load_config(self):
        if self._config:
            return self._config
        config_path = Path(settings.BASE_DIR) / "apps" / "ai" / "models" / "light_model_v1.json"
        with config_path.open("r", encoding="utf-8") as handle:
            self._config = json.load(handle)
        return self._config

    def _predict_progress_pct(self, data):
        config = self._load_config()
        weights = config["progress_pct"]["weights"]
        caps = config["progress_pct"]["caps"]
        total = data.get("cabling_nodes_total")
        ok = data.get("cabling_nodes_ok")
        score = 0.0
        used = 0

        if ok is not None:
            if total and float(total) > 0:
                ratio = min(float(ok) / float(total), 1.0)
            else:
                ratio = min(float(ok) / float(caps["cabling_nodes_ok"]), 1.0)
            score += ratio * weights["cabling_nodes_ok"]
            used += 1

        for key in ["racks_installed", "security_devices", "materials_count"]:
            value = data.get(key)
            if value is None:
                continue
            ratio = min(float(value) / float(caps[key]), 1.0)
            score += ratio * weights[key]
            used += 1

        if used == 0:
            return None, None
        progress = max(0, min(int(round(score * 100)), 100))
        confidence = min(0.35 + (0.15 * used), 0.85)
        return progress, confidence

    def _predict_incidents_severity(self, data):
        config = self._load_config()
        thresholds = config["incidents_severity"]["thresholds"]
        count = data.get("incidents_count")
        if count is None:
            return None, None
        try:
            count_val = int(count)
        except (TypeError, ValueError):
            return None, None
        if count_val >= thresholds["high"]:
            return "high", 0.7
        if count_val >= thresholds["medium"]:
            return "medium", 0.55
        if count_val > 0:
            return "low", 0.4
        return None, None

    def suggest(self, step, data):
        suggestions = []
        if step == 2 and not data.get("progress_pct"):
            value, confidence = self._predict_progress_pct(data)
            if value is not None:
                suggestions.append(
                    {
                        "field": "progress_pct",
                        "value": value,
                        "confidence": confidence,
                        "reason": "Modelo ligero basado en avance técnico.",
                        "tier": "light",
                    }
                )
        if step == 10 and data.get("incidents") and not data.get("incidents_severity"):
            value, confidence = self._predict_incidents_severity(data)
            if value:
                suggestions.append(
                    {
                        "field": "incidents_severity",
                        "value": value,
                        "confidence": confidence,
                        "reason": "Modelo ligero basado en cantidad de incidentes.",
                        "tier": "light",
                    }
                )
        return suggestions


class RuleProvider(BaseAiProvider):
    name = "rule_engine"
    version = "v1"

    def suggest(self, step, data):
        suggestions = []
        if step == 2 and not data.get("progress_pct"):
            suggestions.append(
                {
                    "field": "progress_pct",
                    "value": 0,
                    "confidence": 0.4,
                    "reason": "Sin avance reportado, se sugiere 0.",
                    "tier": "rule",
                }
            )
        if step == 10 and str(data.get("incidents")).lower() == "true":
            if not data.get("incidents_severity"):
                suggestions.append(
                    {
                        "field": "incidents_severity",
                        "value": "medium",
                        "confidence": 0.6,
                        "reason": "Severidad sugerida por default.",
                        "tier": "rule",
                    }
                )
        if step == 7 and str(data.get("missing_materials")).lower() == "true":
            if not data.get("missing_materials_detail"):
                suggestions.append(
                    {
                        "field": "missing_materials_detail",
                        "value": "Pendiente de confirmar",
                        "confidence": 0.3,
                        "reason": "Detalle requerido cuando hay faltantes.",
                        "tier": "rule",
                    }
                )
        return suggestions


class HeavyProvider(BaseAiProvider):
    name = "heavy_model"
    version = "v1"

    def suggest(self, step, data):
        light_provider = LightModelProvider()
        suggestions = [
            {**item, "tier": "heavy"} for item in light_provider.suggest(step, data)
        ]
        if step == 1 and not data.get("site_city"):
            suggestions.append(
                {
                    "field": "site_city",
                    "value": "Ciudad de Mexico",
                    "confidence": 0.35,
                    "reason": "Sugerencia base para datos incompletos.",
                    "tier": "heavy",
                }
            )
        return suggestions
