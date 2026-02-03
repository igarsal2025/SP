const STORAGE_KEY = "sitec_wizard_draft";
const DB_NAME = "sitec_wizard_db";
const DB_VERSION = 2; // Incrementado para agregar cifrado
const API = {
  saveStep: "/api/wizard/steps/save/",
  validate: "/api/wizard/validate/",
  sync: "/api/wizard/sync/",
};
const AI_API = {
  contract: "/api/ai/contract/",
  suggest: "/api/ai/suggest/",
  suggestionStatus: "/api/ai/suggestions/",
};
const SCHEMA_URL = "/api/wizard/schema/";

// Inicializar sync manager y tracker
let syncManager = null;
let syncTracker = null;
let wizardAnalytics = null;
let wizardSchema = null;
let aiPolling = null;
const components = window.SitecComponents || null;
let latestPdfToken = null;
let currentProfile = null;

if (!components) {
  console.warn("[Wizard] SitecComponents no esta disponible.");
}

if (window.SyncManager && window.SyncStatusTracker) {
  syncManager = new window.SyncManager();
  syncTracker = new window.SyncStatusTracker();
}

if (window.WizardAnalytics) {
  wizardAnalytics = new window.WizardAnalytics();
}

async function loadWizardSchema() {
  if (wizardSchema) return wizardSchema;
  const preferredVersion = getPreferredSchemaVersion();
  const url = preferredVersion ? `${SCHEMA_URL}?version=${preferredVersion}` : SCHEMA_URL;
  const response = await fetch(url);
  wizardSchema = await response.json();
  const resolvedVersion =
    wizardSchema?.schema_meta?.resolved_version || wizardSchema?.schema_version;
  if (resolvedVersion) {
    const store = getDraftStore();
    store.schema_version = resolvedVersion;
    saveDraftStore(store);
  }
  return wizardSchema;
}

async function getCurrentProfile() {
  if (currentProfile) return currentProfile;
  try {
    const response = await fetch("/api/users/me/", {
      credentials: "include", // Incluir cookies de sesión
    });
    if (!response.ok) {
      if (response.status === 401) {
        // Usuario no autenticado, redirigir al login
        console.warn("[Wizard] Sesión expirada, redirigiendo al login");
        window.location.href = "/";
        return null;
      }
      // 403 u otros errores: usuario autenticado pero sin permisos o error del servidor
      // No redirigir para evitar bucles infinitos
      return null;
    }
    currentProfile = await response.json();
    return currentProfile;
  } catch (error) {
    console.warn("[Wizard] Error obteniendo perfil:", error);
    return null;
  }
}

async function renderWizardStep(step) {
  const schema = await loadWizardSchema();
  const stepSchema = schema.steps?.[String(step)];
  const container = document.getElementById("wizardDynamicContainer");
  if (!container) return;
  container.innerHTML = "";
  if (!stepSchema) return;
  if (!components || !components.createField) return;

  // Evaluar permiso para ver este paso
  const stepAction = `wizard.step.${step}.view`;
  if (window.permissionsManager) {
    const stepPermission = await window.permissionsManager.evaluate(stepAction);
    if (!stepPermission.allowed) {
      container.innerHTML = `
        <div class="alert alert--error">
          <strong>Acceso denegado</strong>
          <p>No tienes permisos para ver este paso del wizard.</p>
        </div>
      `;
      return;
    }
  }

  const sections = stepSchema.sections || [
    { title: stepSchema.title || `Paso ${step}`, fields: stepSchema.fields || [] },
  ];

  for (const [index, section] of sections.entries()) {
    // Evaluar permiso para ver esta sección
    const sectionAction = `wizard.step.${step}.section.${index + 1}.view`;
    let sectionAllowed = true;
    if (window.permissionsManager && section.permission) {
      const sectionPermission = await window.permissionsManager.evaluate(
        section.permission || sectionAction
      );
      sectionAllowed = sectionPermission.allowed;
    }

    if (!sectionAllowed) {
      continue; // Omitir esta sección si no tiene permiso
    }

    const panel = document.createElement("details");
    panel.className = "wizard__panel wizard__section";
    panel.dataset.section = `step_${step}_section_${index + 1}`;
    panel.open = true;
    if (section.show_if) {
      panel.dataset.showRule = JSON.stringify({
        mode: "all",
        conditions: Object.entries(section.show_if).map(([dep, value]) => ({ field: dep, value })),
      });
    }
    if (section.show_if_any) {
      panel.dataset.showRule = JSON.stringify({
        mode: "any",
        conditions: section.show_if_any || [],
      });
    }
    if (section.show_if_all) {
      panel.dataset.showRule = JSON.stringify({
        mode: "all",
        conditions: section.show_if_all || [],
      });
    }

    const summary = document.createElement("summary");
    summary.className = "panel-title";
    summary.textContent = section.title || stepSchema.title || `Paso ${step}`;
    panel.appendChild(summary);

    const title = document.createElement("div");
    title.className = "panel-title";
    title.textContent = section.title || stepSchema.title || `Paso ${step}`;
    panel.appendChild(title);

    const grid = document.createElement("div");
    grid.className = "grid grid-2";
    const fields = section.fields || [];
    const textareas = [];
    
    for (const field of fields) {
      // Evaluar permiso para este campo
      const fieldAction = field.permission || `wizard.step.${step}.field.${field.name}.edit`;
      let fieldAllowed = true;
      if (window.permissionsManager && field.permission !== false) {
        const fieldPermission = await window.permissionsManager.evaluate(fieldAction);
        fieldAllowed = fieldPermission.allowed;
      }

      if (!fieldAllowed) {
        // Mostrar campo como solo lectura si no tiene permiso de edición
        const readOnlyField = { ...field, readonly: true, disabled: true };
        const fieldEl = components.createField(readOnlyField);
        fieldEl.classList.add("field--readonly");
        if (field.type === "textarea") {
          textareas.push(fieldEl);
        } else {
          grid.appendChild(fieldEl);
        }
      } else {
        const fieldEl = components.createField(field);
        if (field.type === "textarea") {
          textareas.push(fieldEl);
        } else {
          grid.appendChild(fieldEl);
        }
      }
    }
    
    if (grid.children.length) panel.appendChild(grid);
    textareas.forEach((fieldEl) => panel.appendChild(fieldEl));

    container.appendChild(panel);
  }
}

async function enhanceWizardComponents() {
  if (!components) return;
  const signatureDateInput = document.querySelector('[name="signature_date"]');
  const signatureMethodInput = document.querySelector('[name="signature_method"]');
  const supervisorRequiredInput = document.querySelector('[name="signature_supervisor_required"]');
  const profile = await getCurrentProfile();
  const role = profile?.role || "";
  if (role === "supervisor" && supervisorRequiredInput && !supervisorRequiredInput.value) {
    supervisorRequiredInput.value = "true";
    supervisorRequiredInput.dispatchEvent(new Event("change"));
  }
  const canEditSignature = (fieldName) => {
    if (role === "admin_empresa" || role === "pm") return true;
    if (role === "tecnico") return fieldName === "signature_tech";
    if (role === "supervisor") return fieldName === "signature_supervisor";
    if (role === "cliente") return fieldName === "signature_client";
    return true;
  };
  const signatureFields = [
    { name: "signature_tech", label: "Firma técnico" },
    { name: "signature_supervisor", label: "Firma supervisor" },
    { name: "signature_client", label: "Firma cliente" },
  ];

  signatureFields.forEach((field) => {
    const input = document.querySelector(`[name="${field.name}"]`);
    if (!input || input.dataset.enhanced === "true") return;
    input.dataset.enhanced = "true";
    input.type = "hidden";
    if (role === "supervisor" && field.name === "signature_supervisor") {
      input.setAttribute("aria-required", "true");
    }
    if (role === "cliente" && field.name === "signature_client") {
      input.setAttribute("aria-required", "true");
    }
    const wrapper = components.createSignaturePad(input, field.label, {
      dateInput: signatureDateInput,
      methodInput: signatureMethodInput,
      exportName: field.name,
      readOnly: !canEditSignature(field.name),
    });
    input.closest(".field")?.appendChild(wrapper);
  });

  const evidenceInput = document.querySelector('[name="evidence_photos"]');
  if (evidenceInput && evidenceInput.dataset.enhanced !== "true") {
    evidenceInput.dataset.enhanced = "true";
    evidenceInput.type = "hidden";
    const wrapper = components.createEvidenceUploader(evidenceInput);
    evidenceInput.closest(".field")?.appendChild(wrapper);
  }

  const geoInput = document.querySelector('[name="evidence_geo"]');
  if (geoInput && geoInput.dataset.enhanced !== "true") {
    geoInput.dataset.enhanced = "true";
    const wrapper = components.createGeoPicker(geoInput);
    geoInput.closest(".field")?.appendChild(wrapper);
  }
}
function openDb() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      const oldVersion = event.oldVersion;
      
      // Migración: agregar store de sync_status si no existe
      if (!db.objectStoreNames.contains("steps")) {
        db.createObjectStore("steps", { keyPath: "step" });
      }
      if (!db.objectStoreNames.contains("outbox")) {
        db.createObjectStore("outbox", { keyPath: "id", autoIncrement: true });
      }
      if (!db.objectStoreNames.contains("sync_status")) {
        db.createObjectStore("sync_status", { keyPath: "step" });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function idbGetStep(step) {
  const db = await openDb();
  return new Promise((resolve) => {
    const tx = db.transaction("steps", "readonly");
    const store = tx.objectStore("steps");
    const req = store.get(step);
    req.onsuccess = () => {
      const result = req.result;
      if (!result) {
        resolve(null);
        return;
      }
      // Descifrar datos si Encryption está disponible
      const decryptedData = window.Encryption ? window.Encryption.decrypt(result.data) : result.data;
      resolve({ ...result, data: decryptedData });
    };
    req.onerror = () => resolve(null);
  });
}

async function idbSetStep(step, data) {
  const db = await openDb();
  return new Promise((resolve) => {
    const tx = db.transaction("steps", "readwrite");
    const store = tx.objectStore("steps");
    // Cifrar datos sensibles si Encryption está disponible
    const encryptedData = window.Encryption ? window.Encryption.encrypt(data) : data;
    store.put({ step, data: encryptedData, updatedAt: new Date().toISOString() });
    tx.oncomplete = () => resolve();
  });
}

async function idbAddOutbox(step, data) {
  const db = await openDb();
  return new Promise((resolve) => {
    const tx = db.transaction("outbox", "readwrite");
    const store = tx.objectStore("outbox");
    store.add({ step, data, createdAt: new Date().toISOString() });
    tx.oncomplete = () => resolve();
  });
}

async function idbGetOutbox() {
  const db = await openDb();
  return new Promise((resolve) => {
    const tx = db.transaction("outbox", "readonly");
    const store = tx.objectStore("outbox");
    const req = store.getAll();
    req.onsuccess = () => resolve(req.result || []);
    req.onerror = () => resolve([]);
  });
}

async function idbClearOutbox() {
  const db = await openDb();
  return new Promise((resolve) => {
    const tx = db.transaction("outbox", "readwrite");
    const store = tx.objectStore("outbox");
    store.clear();
    tx.oncomplete = () => resolve();
  });
}

async function idbUpsertSteps(steps) {
  if (!steps || !steps.length) return;
  const db = await openDb();
  return new Promise((resolve) => {
    const tx = db.transaction("steps", "readwrite");
    const store = tx.objectStore("steps");
    steps.forEach((step) => {
      store.put({
        step: step.step,
        data: step.data || {},
        updatedAt: step.updated_at || new Date().toISOString(),
      });
    });
    tx.oncomplete = () => resolve();
  });
}

function getWizardMeta() {
  const wizard = document.querySelector(".wizard");
  const step = wizard ? parseInt(wizard.dataset.step || "1", 10) : 1;
  const total = wizard ? parseInt(wizard.dataset.total || "12", 10) : 12;
  return { step, total };
}

function getDraftStore() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return { steps: {} };
  }
  try {
    const payload = JSON.parse(raw);
    if (!payload.steps) payload.steps = {};
    return payload;
  } catch {
    return { steps: {} };
  }
}

function saveDraftStore(store) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
}

function getPreferredSchemaVersion() {
  const store = getDraftStore();
  const versions = [];
  if (store.schema_version) {
    const parsed = parseInt(store.schema_version, 10);
    if (!Number.isNaN(parsed)) versions.push(parsed);
  }
  Object.values(store.steps || {}).forEach((step) => {
    const parsed = parseInt(step?.schema_version, 10);
    if (!Number.isNaN(parsed)) versions.push(parsed);
  });
  if (!versions.length) return null;
  return Math.max(...versions);
}

function setSyncStatus(status, timestamp = null) {
  const el = document.getElementById("syncStatus");
  if (el) {
    const statusText = status;
    const timeText = timestamp ? ` (${new Date(timestamp).toLocaleTimeString("es-MX")})` : "";
    el.textContent = `${statusText}${timeText}`;
    el.setAttribute("data-status", status.toLowerCase().replace(/\s+/g, "-"));
    if (timestamp) {
      el.setAttribute("data-timestamp", timestamp);
    }
  }
}

function getDraftPayload() {
  const inputs = document.querySelectorAll("[data-autosave]");
  const payload = {};
  inputs.forEach((input) => {
    payload[input.name] = input.value;
  });
  payload.updatedAt = new Date().toISOString();
  payload.schema_version = wizardSchema?.schema_version || 1;
  return payload;
}

async function saveDraft() {
  // Evaluar permiso para guardar
  if (window.permissionsManager) {
    const savePermission = await window.permissionsManager.evaluate("wizard.save");
    if (!savePermission.allowed) {
      console.warn("[Wizard] Permiso denegado para guardar");
      setSyncStatus("Error: Sin permisos");
      return false;
    }
  }
  const { step } = getWizardMeta();
  const payload = getDraftPayload();
  const store = getDraftStore();
  store.steps[step] = payload;
  store.updatedAt = payload.updatedAt;
  if (payload.schema_version) {
    store.schema_version = payload.schema_version;
  }
  saveDraftStore(store);
  if (wizardAnalytics) {
    wizardAnalytics.trackEvent("draft_saved", {
      step,
      schema_version: payload.schema_version,
      fields: Object.keys(payload).length,
    });
  }
  await idbSetStep(step, payload);
  await idbAddOutbox(step, payload);
  
  // Mostrar timestamp de último guardado
  updateLastSavedTimestamp(payload.updatedAt);
  setSyncStatus("En cola", payload.updatedAt);

  // Verificar permisos antes de validar/sincronizar para evitar bucles infinitos
  let canValidate = true;
  let canSync = true;
  
  if (window.RoleBasedUI) {
    try {
      const context = await window.RoleBasedUI.getUserContext();
      if (context && context.permissions) {
        canValidate = context.permissions["wizard.validate"] || false;
        canSync = context.permissions["wizard.sync"] || false;
      }
    } catch (e) {
      console.warn("[Wizard] Error obteniendo contexto para permisos:", e);
    }
  }

  // Solo validar/sincronizar si tiene permisos
  if (canValidate) {
    try {
      await validateStep(step, payload);
    } catch (e) {
      console.warn("[Wizard] Error en validación:", e);
    }
  } else {
    console.debug("[Wizard] Omitiendo validación: sin permisos");
  }

  if (canSync) {
    try {
      await syncSteps();
    } catch (e) {
      console.warn("[Wizard] Error en sincronización:", e);
      setSyncStatus("Error", payload.updatedAt);
    }
  } else {
    console.debug("[Wizard] Omitiendo sincronización: sin permisos");
    // Si no puede sincronizar, mantener estado "En cola" pero no mostrar error
  }
}

function updateLastSavedTimestamp(timestamp) {
  const el = document.getElementById("lastSaved");
  if (el) {
    const date = new Date(timestamp);
    el.textContent = `Último guardado: ${date.toLocaleString("es-MX")}`;
    el.setAttribute("data-timestamp", timestamp);
  }
}

function loadDraft() {
  const { step } = getWizardMeta();
  const store = getDraftStore();
  const payload = store.steps[step];
  if (!payload) return;
  Object.keys(payload).forEach((key) => {
    const input = document.querySelector(`[name="${key}"]`);
    if (input) input.value = payload[key];
  });
}

function setupAutosave() {
  setInterval(saveDraft, 30000);
}

async function validateStep(step, payload) {
  // Verificar autenticación antes de validar
  const profile = await getCurrentProfile();
  if (!profile) {
    console.warn("[Wizard] Usuario no autenticado, omitiendo validación");
    return;
  }
  
  try {
    const response = await fetch(API.validate, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include", // Incluir cookies de sesión
      body: JSON.stringify({ step, data: payload }),
    });
    if (!response.ok) {
      if (response.status === 401) {
        // Usuario no autenticado, redirigir al login
        console.warn("[Wizard] Sesión expirada, redirigiendo al login");
        window.location.href = "/";
        return;
      } else if (response.status === 403) {
        // Usuario autenticado pero sin permisos - no redirigir, solo mostrar advertencia
        console.warn("[Wizard] Usuario no tiene permisos para validar, omitiendo validación del servidor");
        updateServerValidationStatus(false);
        return;
      }
      updateServerValidationStatus(false);
      return;
    }
    const result = await response.json();
    if (wizardAnalytics) {
      wizardAnalytics.trackEvent("validation_checked", {
        step,
        allowed: !!result.allowed,
        critical: result.critical?.length || 0,
        warnings: result.warnings?.length || 0,
      });
    }
    const warnings = document.getElementById("validationWarnings");
    const critical = document.getElementById("validationCritical");
    if (warnings) {
      warnings.textContent = result.warnings.length
        ? `Warnings: ${result.warnings.join(", ")}`
        : "Sin warnings.";
    }
    if (critical) {
      critical.textContent = result.critical.length
        ? `Errores criticos: ${result.critical.join(", ")}`
        : "Sin errores criticos.";
    }
    applyFieldHints(result);
    applySignatureRequirements(result);
    updateServerValidationStatus(result.allowed);
  } catch {
    // Ignore validation errors
  }
}

function applySignatureRequirements(result) {
  const required = result?.signature_requirements || [];
  if (!required.length) return;
  const fields = ["signature_tech", "signature_supervisor", "signature_client"];
  fields.forEach((name) => {
    if (!required.includes(name)) return;
    const input = document.querySelector(`[name="${name}"]`);
    if (!input) return;
    input.setAttribute("aria-required", "true");
    if (name === "signature_supervisor") {
      const toggle = document.querySelector('[name="signature_supervisor_required"]');
      if (toggle && !toggle.value) {
        toggle.value = "true";
        toggle.dispatchEvent(new Event("change"));
      }
    }
  });
}

function normalizeFieldName(code) {
  return code.replace(/_(required|invalid|missing|not_signed|failed|issue)$/g, "");
}

function applyFieldHints(result) {
  const allInputs = document.querySelectorAll(".input");
  allInputs.forEach((input) => {
    input.classList.remove("input--error", "input--warning");
    const hint = input.closest(".field")?.querySelector(".field-hint");
    if (hint) hint.remove();
  });

  const messageMap = {
    project_name_required: "Nombre del proyecto es obligatorio.",
    week_start_required: "Fecha de inicio de semana es obligatoria.",
    site_address_required: "Direccion del sitio es obligatoria.",
    technician_required: "Tecnico responsable es obligatorio.",
    progress_pct_required: "Porcentaje de avance es obligatorio.",
    progress_pct_invalid: "Porcentaje de avance debe estar entre 0 y 100.",
    schedule_status_missing: "Estado de calendario recomendado.",
    cabling_nodes_total_required: "Total de nodos cableados es obligatorio.",
    cabling_nodes_ok_missing: "Nodos OK recomendado.",
    racks_installed_required: "Racks instalados es obligatorio.",
    rack_order_issue: "Se detecto desorden en racks.",
    security_devices_required: "Dispositivos de seguridad es obligatorio.",
    security_devices_invalid: "Dispositivos de seguridad no puede ser negativo.",
    cameras_offline: "Camaras offline detectadas.",
    special_systems_notes_required: "Notas de sistemas especializados son obligatorias.",
    materials_count_required: "Total de materiales es obligatorio.",
    materials_list_missing: "Lista de materiales recomendada.",
    missing_materials_detail_missing: "Detalle de faltantes recomendado.",
    tests_failed: "Pruebas no aprobadas. Corregir antes de continuar.",
    qa_not_signed: "QA sin firma. Recomendado completar.",
    test_notes_present: "Notas de pruebas registradas.",
    evidence_photos_required: "Evidencias fotografias son obligatorias.",
    evidence_geo_missing: "Geolocalizacion de evidencias recomendada.",
    evidence_ids_present: "IDs de evidencia registrados.",
    incidents_detail_required: "Detalle de incidentes es obligatorio.",
    mitigation_plan_required: "Plan de mitigacion es obligatorio.",
    incidents_count_present: "Incidentes registrados.",
    signature_tech_required: "Firma de tecnico es obligatoria.",
    signature_supervisor_required: "Firma de supervisor es obligatoria.",
    signature_client_required: "Firma de cliente es obligatoria.",
    signature_date_missing: "Fecha de firma recomendada.",
    final_review_ack_required: "Confirmacion final es obligatoria.",
    report_summary_missing: "Resumen final recomendado.",
    client_feedback_present: "Feedback del cliente registrado.",
    cable_type_missing: "Tipo de cable recomendado.",
    power_issue: "Problema en energia detectado.",
    security_notes_present: "Observaciones de seguridad registradas.",
    special_systems_type_missing: "Tipo de sistema recomendado.",
  };

  const addHint = (fieldName, message, className) => {
    const input = document.querySelector(`[name="${fieldName}"]`);
    if (!input) return;
    input.classList.add(className);
    input.setAttribute("aria-invalid", className === "input--error" ? "true" : "false");
    const field = input.closest(".field");
    if (!field) return;
    const hint = document.createElement("div");
    hint.className = "field-hint";
    const hintId = `${fieldName}-hint`;
    hint.id = hintId;
    input.setAttribute("aria-describedby", hintId);
    hint.textContent = message;
    field.appendChild(hint);
  };

  result.critical.forEach((code) => {
    const fieldName = normalizeFieldName(code);
    const message = messageMap[code] || `Error: ${code}`;
    addHint(fieldName, message, "input--error");
  });
  result.warnings.forEach((code) => {
    const fieldName = normalizeFieldName(code);
    const message = messageMap[code] || `Aviso: ${code}`;
    addHint(fieldName, message, "input--warning");
  });

  updateLocalValidationStatus();
  updateSectionProgress();
}

function ruleMatches(rule) {
  if (!rule) return true;
  const trimmed = rule.trim();
  if (trimmed.startsWith("{")) {
    try {
      const parsed = JSON.parse(trimmed);
      const mode = parsed.mode || "all";
      const conditions = parsed.conditions || [];
      const results = conditions.map((condition) => {
        const input = document.querySelector(`[name="${condition.field}"]`);
        if (!input) return false;
        return input.value === condition.value;
      });
      return mode === "any" ? results.some(Boolean) : results.every(Boolean);
    } catch {
      return true;
    }
  }
  const parts = rule.split(",").map((entry) => entry.trim());
  return parts.every((entry) => {
    const [field, expected] = entry.split("=");
    const input = document.querySelector(`[name="${field}"]`);
    if (!input) return false;
    return input.value === expected;
  });
}

function applyConditionalDisplay() {
  document.querySelectorAll("[data-show-rule], [data-show-when], [data-show-if]").forEach((el) => {
    const rule = el.dataset.showRule || el.dataset.showWhen || el.dataset.showIf;
    const matches = ruleMatches(rule);
    el.style.display = matches ? "" : "none";
  });

  document.querySelectorAll("[data-required-rule]").forEach((input) => {
    const matches = ruleMatches(input.dataset.requiredRule);
    if (matches) {
      input.setAttribute("aria-required", "true");
    } else {
      input.removeAttribute("aria-required");
      input.classList.remove("input--error", "input--warning");
    }
  });
}

function updateLocalValidationStatus() {
  const badge = document.getElementById("localValidationStatus");
  if (!badge) return;
  const requiredInputs = Array.from(document.querySelectorAll("[aria-required='true']"))
    .filter((input) => input.closest(".field")?.style.display !== "none")
    .filter((input) => {
      if (!input.dataset.requiredRule) return true;
      return ruleMatches(input.dataset.requiredRule);
    });
  const missing = requiredInputs.filter((input) => !input.value);
  const invalid = Array.from(document.querySelectorAll("[data-autosave]")).filter((input) => {
    if (!input.value) return false;
    return !input.validity.valid;
  });
  applyLocalConstraintHints();
  badge.textContent = missing.length
    ? `Validacion local: faltan ${missing.length}`
    : invalid.length
    ? `Validacion local: ${invalid.length} invalidos`
    : "Validacion local: completa";
}

function updateServerValidationStatus(allowed) {
  const badge = document.getElementById("serverValidationStatus");
  if (!badge) return;
  badge.textContent = allowed ? "Validacion servidor: OK" : "Validacion servidor: errores";
}

function applyLocalConstraintHints() {
  document.querySelectorAll(".field-hint--local").forEach((hint) => hint.remove());
  document.querySelectorAll("[data-local-invalid='true']").forEach((input) => {
    input.classList.remove("input--warning");
    input.removeAttribute("data-local-invalid");
  });
  document.querySelectorAll("[data-autosave]").forEach((input) => {
    if (!input.value) return;
    if (input.validity.valid) return;
    const field = input.closest(".field");
    if (!field) return;
    if (field.querySelector(".field-hint") && !field.querySelector(".field-hint--local")) {
      return;
    }
    const hint = document.createElement("div");
    hint.className = "field-hint field-hint--local";
    if (input.validity.patternMismatch) {
      hint.textContent = "Formato invalido.";
    } else if (input.validity.rangeUnderflow || input.validity.rangeOverflow) {
      hint.textContent = "Valor fuera de rango.";
    } else {
      hint.textContent = "Dato invalido.";
    }
    field.appendChild(hint);
    input.classList.add("input--warning");
    input.dataset.localInvalid = "true";
  });
}

function updateSectionProgress() {
  const badge = document.getElementById("sectionProgressStatus");
  if (!badge) return;
  const sections = document.querySelectorAll(".wizard__section");
  let total = 0;
  let done = 0;
  sections.forEach((section) => {
    const requiredInputs = Array.from(
      section.querySelectorAll("[aria-required='true']")
    )
      .filter((input) => input.closest(".field")?.style.display !== "none")
      .filter((input) => {
        if (!input.dataset.requiredRule) return true;
        return ruleMatches(input.dataset.requiredRule);
      });
    if (!requiredInputs.length) return;
    total += 1;
    const missing = requiredInputs.filter((input) => !input.value);
    if (!missing.length) done += 1;
  });
  badge.textContent = total ? `Progreso secciones: ${done}/${total}` : "Progreso secciones: --";
}

function buildStepsArray() {
  return [];
}

// Feedback triple: visual, vibración y sonido
function triggerCriticalFeedback(message) {
  // Visual: ya está manejado por los banners
  // Vibración (si está disponible)
  if (navigator.vibrate) {
    navigator.vibrate([100, 50, 100]);
  }
  // Sonido (opcional, no intrusivo)
  // Puede agregarse un sonido sutil aquí si se desea
}

// Re-autenticación antes de acciones críticas
async function requireReauthentication() {
  return new Promise((resolve, reject) => {
    const password = prompt("Por seguridad, ingrese su contraseña para continuar:");
    if (!password) {
      reject(new Error("Re-autenticación cancelada"));
      return;
    }
    
    fetch("/api/wizard/verify-password/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error("Contraseña incorrecta");
        }
      })
      .then((data) => {
        if (data.verified) {
          resolve();
        } else {
          reject(new Error(data.error || "Contraseña incorrecta"));
        }
      })
      .catch(reject);
  });
}

// Calcular ETA basado en tiempos promedio
async function calculateETA(step) {
  if (!wizardAnalytics) return null;
  
  const avgTime = await wizardAnalytics.getAverageTimeForStep(step);
  if (!avgTime) return null;
  
  const { total } = getWizardMeta();
  const remainingSteps = total - step + 1;
  const estimatedTotal = avgTime * remainingSteps;
  
  const minutes = Math.floor(estimatedTotal / 60);
  const seconds = estimatedTotal % 60;
  
  return minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;
}

async function updateETA(step) {
  const eta = await calculateETA(step);
  const el = document.getElementById("stepEta");
  if (el) {
    el.textContent = eta || "--";
  }
}

async function syncSteps(resolution = null) {
  if (!navigator.onLine) {
    setSyncStatus("Offline");
    if (wizardAnalytics) {
      wizardAnalytics.trackEvent("sync_offline", { has_resolution: !!resolution });
    }
    return;
  }

  const outbox = await idbGetOutbox();
  if (!outbox.length) {
    setSyncStatus("Sincronizado");
    if (syncTracker) {
      syncTracker.clear();
    }
    if (wizardAnalytics) {
      wizardAnalytics.trackEvent("sync_noop", { has_resolution: !!resolution });
    }
    return;
  }

  const latestByStep = {};
  outbox.forEach((item) => {
    latestByStep[item.step] = item.data;
  });
  const steps = Object.keys(latestByStep).map((key) => ({
    step: parseInt(key, 10),
    data: latestByStep[key],
  }));

  // Actualizar estado de sync por paso
  if (syncTracker) {
    steps.forEach((s) => syncTracker.setStatus(s.step, "syncing"));
  }

  setSyncStatus("Sincronizando");
  if (wizardAnalytics) {
    wizardAnalytics.trackEvent("sync_started", {
      steps: steps.length,
      has_resolution: !!resolution,
    });
  }

  try {
    // Usar SyncManager con circuit breaker y reintentos
    const result = syncManager
      ? await syncManager.syncWithRetry(steps, resolution)
      : await fetch(API.sync, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ steps, resolution }),
        }).then((r) => {
          if (!r.ok) {
            if (r.status === 401) {
              // Usuario no autenticado, redirigir al login
              window.location.href = "/";
              throw new Error("Sesión expirada");
            } else if (r.status === 403) {
              // Usuario autenticado pero sin permisos - no redirigir
              throw new Error("Sin permisos para sincronizar");
            }
            throw new Error(`Sync failed: ${r.status} ${r.statusText}`);
          }
          return r.json();
        });

    if (result.conflicts && result.conflicts.length) {
      showConflictBanner(result.conflicts);
      setSyncStatus("Error");
      if (syncTracker) {
        result.conflicts.forEach((c) => {
          const stepValue = typeof c === "string" ? c.replace("step_", "") : c.step;
          const step = parseInt(stepValue, 10);
          syncTracker.setStatus(step, "error", "Conflicto detectado");
        });
      }
      if (wizardAnalytics) {
        wizardAnalytics.trackEvent("sync_conflict", {
          steps: steps.length,
          conflicts: result.conflicts.length,
        });
      }
      return;
    }

    await idbClearOutbox();
    await idbUpsertSteps(result.updated_steps || []);

    // Marcar pasos como sincronizados
    if (syncTracker) {
      steps.forEach((s) => syncTracker.setStatus(s.step, "synced"));
    }

    hideConflictBanner();
    setSyncStatus("Sincronizado");
    if (wizardAnalytics) {
      wizardAnalytics.trackEvent("sync_success", { steps: steps.length });
    }
  } catch (error) {
    console.error("[Wizard] Error en sync:", error);
    setSyncStatus("Error");
    if (syncTracker) {
      steps.forEach((s) => syncTracker.setStatus(s.step, "error", error.message));
    }
    if (wizardAnalytics) {
      wizardAnalytics.trackEvent("sync_error", {
        steps: steps.length,
        message: error.message || "unknown",
      });
    }
  }
}

function setupFieldMode() {
  const btn = document.getElementById("btnFieldMode");
  if (!btn) return;
  
  // Cargar preferencia guardada
  loadFieldModePreference();
  
  btn.addEventListener("click", async () => {
    const root = document.documentElement;
    const isFieldMode = root.getAttribute("data-mode") === "field";
    
    if (isFieldMode) {
      root.removeAttribute("data-mode");
    } else {
      root.setAttribute("data-mode", "field");
    }
    if (wizardAnalytics) {
      wizardAnalytics.trackEvent("field_mode_toggle", { enabled: !isFieldMode });
    }
    
    // Guardar preferencia
    await saveFieldModePreference(!isFieldMode);
  });
}

async function loadFieldModePreference() {
  try {
    const profile = await getCurrentProfile();
    if (!profile) return;
    const preferences = profile.preferences || {};
    
    // Si hay preferencia guardada y no es automático, aplicarla
    if (preferences.field_mode !== undefined && !preferences.field_mode_auto) {
      const root = document.documentElement;
      if (preferences.field_mode) {
        root.setAttribute("data-mode", "field");
      } else {
        root.removeAttribute("data-mode");
      }
    }
  } catch (error) {
    console.warn("[Wizard] No se pudo cargar preferencia de Modo Campo:", error);
  }
}

async function saveFieldModePreference(enabled) {
  try {
    const response = await fetch("/api/users/me/", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      credentials: "include", // Incluir cookies de sesión
      body: JSON.stringify({
        preferences: {
          field_mode: enabled,
          field_mode_auto: false, // Usuario desactivó el automático
        },
      }),
    });
    if (!response.ok) {
      if (response.status === 401) {
        console.warn("[Wizard] Sesión expirada, no se pudo guardar preferencia");
        window.location.href = "/";
        return;
      } else if (response.status === 403) {
        console.warn("[Wizard] Sin permisos para guardar preferencia");
        return;
      }
      console.warn("[Wizard] No se pudo guardar preferencia de Modo Campo");
    }
  } catch (error) {
    console.warn("[Wizard] Error guardando preferencia:", error);
  }
}

function shouldEnableFieldModeByTime() {
  const hour = new Date().getHours();
  return hour >= 18 || hour <= 6;
}

function shouldEnableFieldModeByLocation() {
  // No solicitar geolocalización automáticamente (requiere gesto del usuario)
  // Esta función solo se ejecutará cuando el usuario interactúe explícitamente
  return Promise.resolve(false);
}

async function applyAutoFieldMode() {
  // Verificar si el usuario desactivó el modo automático
  try {
    const profile = await getCurrentProfile();
    if (!profile) {
      return; // Usuario no autenticado
    }
    
    const preferences = profile.preferences || {};
    
    // Si el usuario desactivó el automático, no aplicar
    if (preferences.field_mode_auto === false) {
      return;
    }
    
    // Si hay preferencia manual, respetarla
    if (preferences.field_mode !== undefined && !preferences.field_mode_auto) {
      const root = document.documentElement;
      if (preferences.field_mode) {
        root.setAttribute("data-mode", "field");
      }
      return;
    }
  } catch (error) {
    console.warn("[Wizard] No se pudo verificar preferencia:", error);
    return; // Salir si hay error
  }
  
  // Aplicar modo automático si está habilitado
  const root = document.documentElement;
  const byTime = shouldEnableFieldModeByTime();
  // NO usar geolocalización automáticamente (requiere gesto del usuario)
  // byLocation solo se usará cuando el usuario interactúe explícitamente
  if (byTime) {
    root.setAttribute("data-mode", "field");
  }
}

function setupFab() {
  const btn = document.getElementById("fabActions");
  const menu = document.getElementById("fabMenu");
  if (!btn || !menu) return;
  btn.addEventListener("click", () => {
    menu.classList.toggle("open");
  });
}

function setPdfStatus(text, level = "info") {
  const status = document.getElementById("pdfStatus");
  if (!status) return;
  status.textContent = text;
  status.setAttribute("data-level", level);
}

function togglePdfDownload(url) {
  const link = document.getElementById("pdfDownload");
  if (!link) return;
  if (url) {
    link.href = url;
    link.style.display = "inline-flex";
  } else {
    link.removeAttribute("href");
    link.style.display = "none";
  }
}

function togglePdfCopyButton(enabled) {
  const button = document.getElementById("btnCopyPdfToken");
  if (!button) return;
  button.style.display = enabled ? "inline-flex" : "none";
  button.disabled = !enabled;
}

function setPdfMeta(documentPayload) {
  const meta = document.getElementById("pdfMeta");
  if (!meta) return;
  if (!documentPayload) {
    meta.style.display = "none";
    meta.textContent = "";
    latestPdfToken = null;
    togglePdfCopyButton(false);
    return;
  }
  const version = documentPayload.version ?? "--";
  const issuedAt = documentPayload.issued_at
    ? new Date(documentPayload.issued_at).toLocaleString("es-MX")
    : "--";
  const qrToken = documentPayload.qr_token || "--";
  latestPdfToken = documentPayload.qr_token || null;
  togglePdfCopyButton(Boolean(latestPdfToken));
  meta.textContent = `Version ${version} • Emitido: ${issuedAt} • QR: ${qrToken}`;
  meta.style.display = "inline-flex";
}

async function fetchDocumentStatus(documentId) {
  const response = await fetch(`/api/documents/documents/${documentId}/`);
  if (!response.ok) {
    throw new Error("No se pudo obtener estado del documento");
  }
  return response.json();
}

async function fetchLatestDocument(reportId) {
  const response = await fetch(`/api/documents/documents/?report=${reportId}`);
  if (!response.ok) {
    throw new Error("No se pudo obtener el listado de documentos");
  }
  const results = await response.json();
  if (!Array.isArray(results) || !results.length) {
    return null;
  }
  return results[0];
}

async function pollDocument(documentId, attempts = 12) {
  let remaining = attempts;
  const interval = setInterval(async () => {
    if (remaining <= 0) {
      clearInterval(interval);
      setPdfStatus("Tiempo de espera agotado", "warning");
      return;
    }
    remaining -= 1;
    try {
      const doc = await fetchDocumentStatus(documentId);
      if (doc.status === "ready") {
        clearInterval(interval);
        setPdfStatus("PDF listo", "success");
        togglePdfDownload(`/api/documents/documents/${doc.id}/download/`);
        setPdfMeta(doc);
      } else if (doc.status === "failed") {
        clearInterval(interval);
        setPdfStatus("Error al generar PDF", "error");
        setPdfMeta(doc);
      } else {
        setPdfStatus("Generando PDF...", "info");
        setPdfMeta(doc);
      }
    } catch {
      // ignore polling errors
    }
  }, 5000);
}

async function bootstrapPdfStatus(reportId) {
  try {
    const doc = await fetchLatestDocument(reportId);
    if (!doc) {
      setPdfStatus("Sin generar", "info");
      togglePdfDownload(null);
      return;
    }
    if (doc.status === "ready") {
      setPdfStatus("PDF listo", "success");
      togglePdfDownload(`/api/documents/documents/${doc.id}/download/`);
      setPdfMeta(doc);
      return;
    }
    if (doc.status === "failed") {
      setPdfStatus("Error en ultimo PDF", "error");
      togglePdfDownload(null);
      setPdfMeta(doc);
      return;
    }
    setPdfStatus("PDF en cola", "info");
    setPdfMeta(doc);
    pollDocument(doc.id);
  } catch {
    setPdfStatus("Estado PDF no disponible", "warning");
  }
}

async function generatePdf(reportId) {
  const response = await fetch("/api/documents/documents/report/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ report_id: reportId }),
  });
  if (!response.ok) {
    throw new Error("No se pudo solicitar la generacion del PDF");
  }
  return response.json();
}

function setupPdfPanel() {
  const wizard = document.querySelector(".wizard");
  const reportId = wizard?.dataset?.reportId || "";
  const button = document.getElementById("btnGeneratePdf");
  const copyButton = document.getElementById("btnCopyPdfToken");

  if (!button) return;
  if (!reportId) {
    button.disabled = true;
    setPdfStatus("Reporte no asociado", "warning");
    togglePdfCopyButton(false);
    return;
  }

  bootstrapPdfStatus(reportId);

  if (copyButton) {
    copyButton.addEventListener("click", async () => {
      if (!latestPdfToken) return;
      try {
        const host = window.location.host;
        const verifyUrl = `https://${host}/api/documents/verify/${latestPdfToken}/`;
        await navigator.clipboard.writeText(verifyUrl);
        setPdfStatus("Enlace QR copiado", "success");
      } catch {
        setPdfStatus("No se pudo copiar el enlace", "warning");
      }
    });
  }

  button.addEventListener("click", async () => {
    togglePdfDownload(null);
    setPdfStatus("Solicitando PDF...", "info");
    setPdfMeta(null);
    try {
      const documentPayload = await generatePdf(reportId);
      setPdfStatus("PDF en cola", "info");
      setPdfMeta(documentPayload);
      pollDocument(documentPayload.id);
    } catch (error) {
      setPdfStatus(error.message || "Error al generar PDF", "error");
    }
  });
}

function showAiBanner(message) {
  const banner = document.getElementById("aiBanner");
  if (!banner) return;
  banner.style.display = "block";
  banner.textContent = message;
  banner.scrollIntoView({ behavior: "smooth", block: "start" });
}

function hideAiBanner() {
  const banner = document.getElementById("aiBanner");
  if (!banner) return;
  banner.style.display = "none";
  banner.textContent = "";
}

function applyAiSuggestions(suggestions) {
  let applied = 0;
  suggestions.forEach((item) => {
    const input = document.querySelector(`[name="${item.field}"]`);
    if (!input) return;
    if (input.value) return;
    input.value = item.value;
    applied += 1;
  });
  applyConditionalDisplay();
  updateLocalValidationStatus();
  updateSectionProgress();
  if (applied) {
    showAiBanner(`IA aplico ${applied} sugerencias en este paso.`);
  } else {
    showAiBanner("IA no encontro sugerencias aplicables.");
  }
}

async function requestAiSuggestions(mode = "quick") {
  const { step } = getWizardMeta();
  const payload = getDraftPayload();
  hideAiBanner();
  try {
    const response = await fetch(AI_API.suggest, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ step, data: payload, mode }),
    });
    if (!response.ok) {
      showAiBanner("No se pudo obtener sugerencias IA.");
      return;
    }
    const result = await response.json();
    if (result.status === "queued") {
      if (result.suggestion_id) {
        startAiPolling(result.suggestion_id);
      }
      showAiBanner("IA pesada en cola. Se aplicaran sugerencias cuando este lista.");
      return;
    }
    applyAiSuggestions(result.suggestions || []);
  } catch {
    showAiBanner("Error al consultar IA.");
  }
}

function startAiPolling(suggestionId) {
  if (aiPolling) {
    clearInterval(aiPolling);
  }
  let attempts = 0;
  aiPolling = setInterval(async () => {
    attempts += 1;
    if (attempts > 12) {
      clearInterval(aiPolling);
      aiPolling = null;
      showAiBanner("IA pesada no respondio a tiempo.");
      return;
    }
    try {
      const response = await fetch(`${AI_API.suggestionStatus}${suggestionId}/`);
      if (!response.ok) return;
      const result = await response.json();
      if (result.status === "success" && result.output) {
        clearInterval(aiPolling);
        aiPolling = null;
        applyAiSuggestions(result.output.suggestions || []);
      }
    } catch {
      // ignore polling errors
    }
  }, 5000);
}

function setupProgress() {
  const { step, total } = getWizardMeta();
  const el = document.getElementById("wizardProgress");
  if (!el) return;
  const pct = Math.round((step / total) * 100);
  el.style.width = `${pct}%`;
}

function appendAiMessage(text, type = "assistant") {
  const log = document.getElementById("aiChatLog");
  if (!log) return;
  const msg = document.createElement("div");
  msg.className = `ai-chat__message${type === "system" ? " ai-chat__message--system" : ""}`;
  msg.textContent = text;
  log.appendChild(msg);
  log.scrollTop = log.scrollHeight;
}

async function handleAiChatRequest() {
  const input = document.getElementById("aiChatInput");
  if (!input) return;
  const query = input.value.trim();
  if (!query) return;
  input.value = "";
  appendAiMessage(`Usuario: ${query}`, "system");

  const { step } = getWizardMeta();
  const payload = getDraftPayload();
  try {
    const response = await fetch(AI_API.suggest, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ step, data: payload, mode: "quick" }),
    });
    if (!response.ok) {
      appendAiMessage("No se pudo consultar IA.", "system");
      return;
    }
    const result = await response.json();
    const suggestions = result.suggestions || [];
    if (!suggestions.length) {
      appendAiMessage("IA: No hay sugerencias para este paso.");
      return;
    }
    applyAiSuggestions(suggestions);
    suggestions.forEach((item) => {
      appendAiMessage(
        `IA aplico ${item.field} = ${item.value} (confianza ${Math.round(
          (item.confidence || 0) * 100
        )}%).`
      );
    });
  } catch {
    appendAiMessage("Error al consultar IA.", "system");
  }
}

function setupAiChat() {
  const input = document.getElementById("aiChatInput");
  const button = document.getElementById("aiChatSend");
  if (!input || !button) return;
  button.addEventListener("click", handleAiChatRequest);
  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      handleAiChatRequest();
    }
  });
}

async function applyWizardVisibility() {
  // Obtener contexto del usuario
  let userContext = null;
  if (window.RoleBasedUI) {
    userContext = await window.RoleBasedUI.getUserContext();
  }
  
  if (!userContext || !userContext.ui_config) {
    console.warn("[Wizard] No se pudo obtener contexto del usuario");
    return;
  }
  
  const uiConfig = userContext.ui_config;
  const wizard = document.querySelector(".wizard");
  
  // Si es modo readonly, deshabilitar todos los campos
  if (uiConfig.wizard_mode === "readonly" || wizard?.classList.contains("wizard--readonly")) {
    document.querySelectorAll(".wizard input, .wizard textarea, .wizard select").forEach((el) => {
      el.disabled = true;
      el.readOnly = true;
    });
    return;
  }
  
  // Ocultar botón de modo campo si no tiene permiso
  const btnFieldMode = document.getElementById("btnFieldMode");
  if (btnFieldMode && !uiConfig.can_use_field_mode) {
    btnFieldMode.style.display = "none";
  }
  
  // Ocultar componentes avanzados según rol (solo admin, PM, supervisor)
  const role = userContext.profile?.role;
  const advancedPanel = document.querySelector('[data-wizard-component="advanced"]');
  if (advancedPanel && role !== "admin_empresa" && role !== "pm" && role !== "supervisor") {
    advancedPanel.style.display = "none";
  }
  
  // Ocultar chatbot IA si no tiene permiso
  const aiChatPanel = document.querySelector('[data-wizard-component="ai-chat"]');
  if (aiChatPanel && !uiConfig.can_use_ai_chat) {
    aiChatPanel.style.display = "none";
  }
  
  // Ocultar panel de PDF si no tiene permiso
  const pdfPanel = document.querySelector('[data-wizard-component="pdf"]');
  if (pdfPanel && !uiConfig.can_generate_pdf) {
    pdfPanel.style.display = "none";
  }
  
  // Ocultar FAB si no tiene permisos relevantes
  const fab = document.querySelector(".fab");
  if (fab) {
    const fabAiSuggest = document.getElementById("fabAiSuggest");
    if (fabAiSuggest && !uiConfig.can_use_ai_chat) {
      fabAiSuggest.style.display = "none";
    }
    
    // Si no hay elementos visibles en el FAB, ocultarlo
    const visibleItems = fab.querySelectorAll(".fab__item:not([style*='display: none'])");
    if (visibleItems.length === 0) {
      fab.style.display = "none";
    }
  }
}

async function applyPermissionsToNavigation() {
  if (!window.permissionsManager) return;
  
  const { step, total } = getWizardMeta();
  const btnPrev = document.getElementById("btnPrev");
  const btnNext = document.getElementById("btnNext");
  const btnSave = document.getElementById("btnSave");
  
  // Evaluar permisos para navegación
  const permissions = await window.permissionsManager.evaluateMultiple([
    "wizard.save",
    step > 1 ? `wizard.step.${step - 1}.view` : null,
    step < total ? `wizard.step.${step + 1}.view` : null,
  ].filter(Boolean));
  
  // Aplicar permisos a botones
  if (btnSave) {
    const saveAllowed = permissions.get("wizard.save")?.allowed ?? true;
    if (!saveAllowed) {
      btnSave.disabled = true;
      btnSave.title = "No tienes permisos para guardar";
    }
  }
  
  if (btnPrev && step > 1) {
    const prevStepAction = `wizard.step.${step - 1}.view`;
    const prevAllowed = permissions.get(prevStepAction)?.allowed ?? true;
    if (!prevAllowed) {
      btnPrev.disabled = true;
      btnPrev.title = "No tienes permisos para ver el paso anterior";
    }
  }
  
  if (btnNext && step < total) {
    const nextStepAction = `wizard.step.${step + 1}.view`;
    const nextAllowed = permissions.get(nextStepAction)?.allowed ?? true;
    if (!nextAllowed) {
      btnNext.disabled = true;
      btnNext.title = "No tienes permisos para ver el siguiente paso";
    }
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  // Verificar si el usuario está autenticado antes de inicializar
  const wizardSection = document.querySelector(".wizard");
  if (!wizardSection) {
    // Usuario no autenticado, no inicializar wizard
    console.log("[Wizard] Usuario no autenticado, wizard no inicializado");
    return;
  }
  if (!document.querySelector(".wizard")) {
    return;
  }
  setupAutosave();
  setupFieldMode();
  applyAutoFieldMode();
  setupFab();
  setupProgress();
  setSyncStatus(navigator.onLine ? "Sincronizado" : "Offline");
  
  const { step } = getWizardMeta();

  await renderWizardStep(step);
  loadDraft();
  await enhanceWizardComponents();
  await applyPermissionsToNavigation();
  
  // Aplicar visibilidad según contexto del usuario
  await applyWizardVisibility();
  
  // Iniciar analytics para este paso
  if (wizardAnalytics) {
    wizardAnalytics.startStep(step);
    updateETA(step);
    wizardAnalytics.trackEvent("wizard_loaded", {
      step,
      schema_version: wizardSchema?.schema_version || 1,
    });
  }
  
  // Verificar autenticación antes de validar
  getCurrentProfile().then((profile) => {
    if (!profile) {
      console.warn("[Wizard] Usuario no autenticado, omitiendo validación inicial");
      // Aún cargar datos locales aunque no esté autenticado
      idbGetStep(step).then((record) => {
        if (record && record.data) {
          Object.keys(record.data).forEach((key) => {
            const input = document.querySelector(`[name="${key}"]`);
            if (input) input.value = record.data[key];
          });
        }
        applyConditionalDisplay();
        updateLocalValidationStatus();
        updateSectionProgress();
      });
      return;
    }
    
    idbGetStep(step).then((record) => {
      if (record && record.data) {
        Object.keys(record.data).forEach((key) => {
          const input = document.querySelector(`[name="${key}"]`);
          if (input) input.value = record.data[key];
        });
        validateStep(step, record.data);
        if (record.updatedAt) {
          updateLastSavedTimestamp(record.updatedAt);
        }
      } else {
        const payload = getDraftPayload();
        validateStep(step, payload);
      }
      applyConditionalDisplay();
      updateLocalValidationStatus();
      updateSectionProgress();
    });
  });
  
  window.addEventListener("online", () => {
    syncSteps().catch(() => setSyncStatus("Error"));
    if (wizardAnalytics) {
      wizardAnalytics.trackEvent("network_online");
    }
  });
  window.addEventListener("offline", () => {
    if (wizardAnalytics) {
      wizardAnalytics.trackEvent("network_offline");
    }
  });
  
  // Enviar analytics al salir de la página
  window.addEventListener("beforeunload", () => {
    if (wizardAnalytics) {
      wizardAnalytics.trackEvent("wizard_unload", { step });
      wizardAnalytics.endStep(step);
      wizardAnalytics.sendToServer();
    }
  });
  
  if (components && components.startAdvancedComponents) {
    const wizard = document.querySelector(".wizard");
    const projectId = wizard?.dataset?.projectId || "";
    const refreshRaw = wizard?.dataset?.refreshMs;
    const refreshMs = refreshRaw ? parseInt(refreshRaw, 10) : 60000;
    const normalizedRefresh = Number.isNaN(refreshMs) ? 60000 : refreshMs;
    components.startAdvancedComponents(projectId, { refreshMs: normalizedRefresh });
  }

  setupPdfPanel();
  setupAiChat();

  setupNavigation();

  document.querySelectorAll(".input").forEach((input) => {
    input.addEventListener("change", () => {
      applyConditionalDisplay();
      updateLocalValidationStatus();
      updateSectionProgress();
    });
  });

  const aiButton = document.getElementById("fabAiSuggest");
  if (aiButton) {
    aiButton.addEventListener("click", () => requestAiSuggestions("quick"));
  }
});

async function setupNavigation() {
  const btnPrev = document.getElementById("btnPrev");
  const btnNext = document.getElementById("btnNext");
  const btnSave = document.getElementById("btnSave");
  const { step, total } = getWizardMeta();

  if (btnSave) {
    btnSave.addEventListener("click", async () => {
      // Evaluar permiso para guardar
      if (window.permissionsManager) {
        const savePermission = await window.permissionsManager.evaluate("wizard.save");
        if (!savePermission.allowed) {
          alert("No tienes permisos para guardar este paso.");
          return;
        }
      }
      await saveDraft();
    });
  }

  if (btnPrev) {
    btnPrev.disabled = step <= 1;
    btnPrev.addEventListener("click", () => {
      const prev = Math.max(1, step - 1);
      window.location.href = `/wizard/${prev}/`;
    });
  }

  if (btnNext) {
    btnNext.disabled = step >= total;
    btnNext.addEventListener("click", async () => {
      // Evaluar permiso para avanzar al siguiente paso
      const nextStep = step + 1;
      const nextStepAction = `wizard.step.${nextStep}.view`;
      if (window.permissionsManager) {
        const nextStepPermission = await window.permissionsManager.evaluate(nextStepAction);
        if (!nextStepPermission.allowed) {
          alert(`No tienes permisos para acceder al paso ${nextStep}.`);
          return;
        }
      }

      const payload = getDraftPayload();
      await saveDraft();
      
      // Re-autenticación antes de paso 11 (firmas) o paso 12 (envío final)
      if (step === 10 || step === 11) {
        try {
          await requireReauthentication();
        } catch (error) {
          alert("Re-autenticación requerida. " + error.message);
          triggerCriticalFeedback("Re-autenticación fallida");
          return;
        }
      }
      
      const validation = await fetch(API.validate, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ step, data: payload }),
      });
      if (!validation.ok) {
        setSyncStatus("Error");
        showValidationBanner(["Sesión requerida. Inicia sesión e intenta de nuevo."]);
        updateServerValidationStatus(false);
        return;
      }
      const result = await validation.json();
      if (!result.allowed) {
        setSyncStatus("Error");
        showValidationBanner(result.critical);
        triggerCriticalFeedback("Errores críticos detectados");
        updateServerValidationStatus(false);
        return;
      }
      
      // Finalizar analytics del paso actual
      if (wizardAnalytics) {
        wizardAnalytics.endStep(step);
      }
      
      hideValidationBanner();
      updateServerValidationStatus(true);
      const next = Math.min(total, step + 1);
      window.location.href = `/wizard/${next}/`;
    });
  }
}

function showValidationBanner(errors) {
  const banner = document.getElementById("validationBanner");
  // Feedback triple en errores críticos
  triggerCriticalFeedback("Errores críticos detectados");
  if (!banner) return;
  banner.style.display = "block";
  banner.textContent = `Errores criticos: ${errors.join(", ")}`;
  banner.scrollIntoView({ behavior: "smooth", block: "start" });
}

function hideValidationBanner() {
  const banner = document.getElementById("validationBanner");
  if (!banner) return;
  banner.style.display = "none";
  banner.textContent = "";
}

function showConflictBanner(conflicts) {
  const banner = document.getElementById("conflictBanner");
  if (!banner) return;
  banner.style.display = "block";
  banner.innerHTML = "";
  const title = document.createElement("div");
  title.className = "conflict-title";
  title.textContent = "Conflictos detectados";
  banner.appendChild(title);

  const labelFromName = (name) =>
    components && components.labelFromName ? components.labelFromName(name) : name;
  const escapeHtml = (value) =>
    String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  const stringifyValue = (value) => {
    if (value === null || value === undefined) return "";
    if (Array.isArray(value)) return value.join(", ");
    if (typeof value === "object") return JSON.stringify(value, null, 2);
    return String(value);
  };
  const truncateValue = (raw, limit = 220) => {
    if (!raw) return "";
    return raw.length > limit ? `${raw.slice(0, limit)}…` : raw;
  };
  const tokenize = (text) => text.split(/(\s+)/);
  const buildDiff = (serverValue, clientValue) => {
    const rawServer = truncateValue(stringifyValue(serverValue));
    const rawClient = truncateValue(stringifyValue(clientValue));
    if (!rawServer && !rawClient) {
      return { server: "--", client: "--" };
    }
    if (rawServer === rawClient) {
      const safe = escapeHtml(rawServer || "--");
      return { server: safe || "--", client: safe || "--" };
    }
    const serverTokens = tokenize(rawServer);
    const clientTokens = tokenize(rawClient);
    if (serverTokens.length * clientTokens.length > 2500) {
      return {
        server: escapeHtml(rawServer || "--"),
        client: escapeHtml(rawClient || "--"),
      };
    }
    const rows = serverTokens.length;
    const cols = clientTokens.length;
    const lcs = Array.from({ length: rows + 1 }, () => Array(cols + 1).fill(0));
    for (let i = rows - 1; i >= 0; i -= 1) {
      for (let j = cols - 1; j >= 0; j -= 1) {
        if (serverTokens[i] === clientTokens[j]) {
          lcs[i][j] = lcs[i + 1][j + 1] + 1;
        } else {
          lcs[i][j] = Math.max(lcs[i + 1][j], lcs[i][j + 1]);
        }
      }
    }
    let i = 0;
    let j = 0;
    let serverHtml = "";
    let clientHtml = "";
    while (i < rows && j < cols) {
      if (serverTokens[i] === clientTokens[j]) {
        const token = escapeHtml(serverTokens[i]);
        serverHtml += token;
        clientHtml += token;
        i += 1;
        j += 1;
        continue;
      }
      if (lcs[i + 1][j] >= lcs[i][j + 1]) {
        serverHtml += `<span class="diff-removed">${escapeHtml(serverTokens[i])}</span>`;
        i += 1;
      } else {
        clientHtml += `<span class="diff-added">${escapeHtml(clientTokens[j])}</span>`;
        j += 1;
      }
    }
    while (i < rows) {
      serverHtml += `<span class="diff-removed">${escapeHtml(serverTokens[i])}</span>`;
      i += 1;
    }
    while (j < cols) {
      clientHtml += `<span class="diff-added">${escapeHtml(clientTokens[j])}</span>`;
      j += 1;
    }
    return {
      server: serverHtml || "--",
      client: clientHtml || "--",
    };
  };

  conflicts.forEach((item) => {
    if (typeof item === "string") {
      const step = item.replace("step_", "");
      const row = document.createElement("div");
      row.className = "conflict-item";
      row.innerHTML = `
        <span>Conflicto en paso ${step}</span>
        <button data-step="${step}" data-choice="client" class="btn btn--secondary">Usar local</button>
        <button data-step="${step}" data-choice="server" class="btn btn--ghost">Usar servidor</button>
      `;
      banner.appendChild(row);
      if (wizardAnalytics) {
        wizardAnalytics.trackEvent("conflict_banner_shown", {
          step: parseInt(step, 10),
          fields: 0,
        });
      }
      return;
    }

    const step = String(item.step);
    const wrapper = document.createElement("div");
    wrapper.className = "conflict-item conflict-item--fields";

    const header = document.createElement("div");
    header.className = "conflict-step";
    header.textContent = `Conflicto en paso ${step}`;
    wrapper.appendChild(header);

    const fields = item.fields || [];
    if (!fields.length) {
      const empty = document.createElement("div");
      empty.className = "helper";
      empty.textContent = "Sin detalles por campo. Selecciona una fuente completa.";
      wrapper.appendChild(empty);
    } else {
      const fieldList = document.createElement("div");
      fieldList.className = "conflict-fields";
      fields.forEach((field) => {
        const row = document.createElement("div");
        row.className = "conflict-field";

        const name = document.createElement("div");
        name.className = "conflict-field__name";
        name.textContent = labelFromName(field.name);
        row.appendChild(name);

        const values = document.createElement("div");
        values.className = "conflict-field__values";
        const diff = buildDiff(field.server, field.client);
        values.innerHTML = `
          <div><span class="helper">Servidor:</span> <span class="conflict-field__value">${diff.server}</span></div>
          <div><span class="helper">Local:</span> <span class="conflict-field__value">${diff.client}</span></div>
        `;
        row.appendChild(values);

        const choices = document.createElement("div");
        choices.className = "conflict-field__choices";
        const clientId = `conflict_${step}_${field.name}_client`;
        const serverId = `conflict_${step}_${field.name}_server`;
        choices.innerHTML = `
          <label class="conflict-choice">
            <input type="radio" name="conflict_${step}_${field.name}" value="client" id="${clientId}" checked />
            <span>Local</span>
          </label>
          <label class="conflict-choice">
            <input type="radio" name="conflict_${step}_${field.name}" value="server" id="${serverId}" />
            <span>Servidor</span>
          </label>
        `;
        row.appendChild(choices);
        fieldList.appendChild(row);
      });
      wrapper.appendChild(fieldList);
    }

    const actions = document.createElement("div");
    actions.className = "conflict-actions";
    actions.innerHTML = `
      <button data-step="${step}" data-choice="client" class="btn btn--secondary">Usar local</button>
      <button data-step="${step}" data-choice="server" class="btn btn--ghost">Usar servidor</button>
      <button data-step="${step}" data-action="merge" class="btn btn--field">Resolver por campo</button>
    `;
    wrapper.appendChild(actions);
    banner.appendChild(wrapper);
    if (wizardAnalytics) {
      wizardAnalytics.trackEvent("conflict_banner_shown", {
        step: parseInt(step, 10),
        fields: fields.length,
      });
    }
  });

  banner.scrollIntoView({ behavior: "smooth", block: "start" });

  banner.querySelectorAll("button[data-choice]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const step = btn.dataset.step;
      const choice = btn.dataset.choice;
      await syncSteps({ [step]: choice });
    });
  });

  banner.querySelectorAll("button[data-action='merge']").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const step = btn.dataset.step;
      const fields = {};
      banner
        .querySelectorAll(`input[type="radio"][name^="conflict_${step}_"]`)
        .forEach((input) => {
          if (!input.checked) return;
          const parts = input.name.split(`conflict_${step}_`);
          const fieldName = parts[1];
          fields[fieldName] = input.value;
        });
      await syncSteps({ [step]: { mode: "merge", fields } });
    });
  });
}

function hideConflictBanner() {
  const banner = document.getElementById("conflictBanner");
  if (!banner) return;
  banner.style.display = "none";
  banner.innerHTML = "";
}
