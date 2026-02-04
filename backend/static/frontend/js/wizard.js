// ===== LOG INMEDIATO FUERA DE LA IIFE =====
// Este log se ejecuta ANTES de cualquier cosa para verificar que el script se carga
console.log("%c[Wizard] 🔥 wizard.js ARCHIVO CARGADO (fuera de IIFE)", "color: red; font-weight: bold; font-size: 18px;");
console.log("[Wizard] Timestamp archivo:", new Date().toISOString());

// Protección contra carga múltiple usando IIFE
// IMPORTANTE: Este script DEBE ejecutarse cuando se carga
(function() {
  'use strict';
  
  // PROTECCIÓN CONTRA DOBLE CARGA - DEBE SER LO PRIMERO
  if (window.__WIZARD_LOADED__) {
    console.warn("[Wizard] ⚠️ wizard.js ya fue cargado, evitando doble carga");
    return; // Salir inmediatamente si ya está cargado
  }
  
  // Establecer flag INMEDIATAMENTE para prevenir doble ejecución
  window.__WIZARD_LOADED__ = true;
  
  try {
    // Log inmediato ANTES de cualquier otra cosa - FORZADO
    if (typeof console !== "undefined") {
      console.log("%c[Wizard] ⚡ wizard.js cargado - INICIO", "color: blue; font-weight: bold; font-size: 16px;");
      console.log("[Wizard] Timestamp:", new Date().toISOString());
      console.log("[Wizard] window.SitecComponents al inicio:", typeof window.SitecComponents);
      console.log("[Wizard] Script ejecutándose en:", window.location.href);
      console.log("[Wizard] ✅ __WIZARD_LOADED__ establecido");
    } else {
      // Fallback si console no está disponible
      alert("Wizard: console no disponible");
    }
  } catch (initError) {
    console.error("[Wizard] ❌ ERROR FATAL en inicialización:", initError);
    console.error("[Wizard] Stack:", initError.stack);
    // No lanzar el error para que el script pueda continuar
  }
  
  try {
  // Constantes y configuración
  const DB_NAME = "sitec_wizard_db";
  const DB_VERSION = 2; // Incrementado para agregar cifrado
  const STORAGE_KEY = "sitec_wizard_draft"; // Clave para localStorage
  const API = {
    saveStep: "/api/wizard/steps/save/",
    validate: "/api/wizard/validate/",
    sync: "/api/wizard/sync/",
  };
  
  /**
   * Obtiene el token CSRF de las cookies
   * @returns {string}
   */
  function getCSRFToken() {
    const name = "csrftoken";
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      const [key, value] = cookie.trim().split("=");
      if (key === name) {
        return decodeURIComponent(value);
      }
    }
    return "";
  }
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
// components se obtiene dinámicamente cuando se necesita
let latestPdfToken = null;
let currentProfile = null;

// Función helper para obtener components
function getComponents() {
  return window.SitecComponents || null;
}

if (!getComponents()) {
  console.warn("[Wizard] SitecComponents no esta disponible al inicio. Se intentará cargar más tarde.");
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
  console.log("[Wizard] Iniciando renderizado del paso", step);
  const schema = await loadWizardSchema();
  console.log("[Wizard] Schema cargado:", schema ? "OK" : "ERROR");
  const stepSchema = schema.steps?.[String(step)];
  console.log("[Wizard] Step schema:", stepSchema ? "OK" : "ERROR");
  const container = document.getElementById("wizardDynamicContainer");
  if (!container) {
    console.error("[Wizard] No se encontró el contenedor wizardDynamicContainer");
    return;
  }
  container.innerHTML = "";
  if (!stepSchema) {
    console.error("[Wizard] No se encontró el schema para el paso", step);
    container.innerHTML = `<div class="alert alert--error">No se encontró el schema para el paso ${step}</div>`;
    return;
  }
  // Verificar components nuevamente (puede haberse cargado después)
  let currentComponents = getComponents();
  if (!currentComponents) {
    console.error("[Wizard] SitecComponents no está disponible. Esperando...");
    // Esperar más tiempo y reintentar varias veces
    for (let i = 0; i < 10; i++) {
      await new Promise(resolve => setTimeout(resolve, 200));
      currentComponents = window.SitecComponents || null;
      if (currentComponents && currentComponents.createField) {
        console.log(`[Wizard] ✅ SitecComponents disponible después de ${(i + 1) * 200}ms`);
        break;
      }
    }
    
    if (!currentComponents || !currentComponents.createField) {
      console.error("[Wizard] SitecComponents aún no está disponible después de esperar");
      console.error("[Wizard] Verificando si components.js se cargó...");
      
      // Verificar si el script está en el DOM
      const componentsScript = Array.from(document.scripts).find(s => 
        s.src && (s.src.includes('components.js') || s.src.endsWith('/components.js'))
      );
      
      if (!componentsScript) {
        console.error("[Wizard] ❌ components.js no está en el DOM");
        container.innerHTML = `<div class="alert alert--error">
          <strong>Error de carga</strong>
          <p>El script components.js no se cargó. Por favor, recarga la página.</p>
          <p style="font-size: 0.875rem; margin-top: 0.5rem;">Si el problema persiste, verifica la consola del navegador.</p>
        </div>`;
        return;
      } else {
        console.error("[Wizard] ⚠️ components.js está en el DOM pero SitecComponents no está disponible");
        console.error("[Wizard] Esto puede indicar un error de sintaxis en components.js");
        container.innerHTML = `<div class="alert alert--error">
          <strong>Error de ejecución</strong>
          <p>components.js se cargó pero no se ejecutó correctamente.</p>
          <p style="font-size: 0.875rem; margin-top: 0.5rem;">Verifica la consola del navegador para ver el error específico.</p>
          <p style="font-size: 0.875rem; margin-top: 0.5rem;">Intenta recargar la página (F5).</p>
        </div>`;
        return;
      }
    }
  }
  
  if (!currentComponents.createField) {
    console.error("[Wizard] components.createField no está disponible");
    console.error("[Wizard] SitecComponents disponible pero sin createField:", Object.keys(currentComponents || {}));
    container.innerHTML = `<div class="alert alert--error">
      <strong>Error de función</strong>
      <p>La función createField no está disponible en SitecComponents.</p>
      <p style="font-size: 0.875rem; margin-top: 0.5rem;">Verifica la consola del navegador para más detalles.</p>
      <p style="font-size: 0.875rem; margin-top: 0.5rem;">Intenta recargar la página (F5).</p>
    </div>`;
    return;
  }
  console.log("[Wizard] Componentes disponibles, renderizando campos...");

  // Evaluar permiso para ver este paso
  const stepAction = `wizard.step.${step}.view`;
  if (window.permissionsManager) {
    try {
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
    } catch (permError) {
      console.warn(`[Wizard] Error evaluando permiso del paso ${step}, continuando sin restricción:`, permError);
      // Continuar sin restricción de permisos si falla la evaluación
    }
  }

  const sections = stepSchema.sections || [
    { title: stepSchema.title || `Paso ${step}`, fields: stepSchema.fields || [] },
  ];

  console.log(`[Wizard] Renderizando ${sections.length} sección(es) para el paso ${step}`);

  for (const [index, section] of sections.entries()) {
    console.log(`[Wizard] Procesando sección ${index + 1}/${sections.length}: "${section.title || 'Sin título'}" con ${(section.fields || []).length} campos`);
    // Evaluar permiso para ver esta sección
    const sectionAction = `wizard.step.${step}.section.${index + 1}.view`;
    let sectionAllowed = true;
    if (window.permissionsManager && section.permission) {
      try {
        const sectionPermission = await window.permissionsManager.evaluate(
          section.permission || sectionAction
        );
        sectionAllowed = sectionPermission.allowed;
      } catch (permError) {
        console.warn(`[Wizard] Error evaluando permiso de sección ${index + 1}, continuando:`, permError);
        // Continuar permitiendo la sección si falla la evaluación
        sectionAllowed = true;
      }
    }

    if (!sectionAllowed) {
      console.log(`[Wizard] Sección ${index + 1} omitida por falta de permisos`);
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
      try {
        // Evaluar permiso para este campo
        const fieldAction = field.permission || `wizard.step.${step}.field.${field.name}.edit`;
        let fieldAllowed = true;
        if (window.permissionsManager && field.permission !== false) {
          try {
            const fieldPermission = await window.permissionsManager.evaluate(fieldAction);
            fieldAllowed = fieldPermission.allowed;
          } catch (permError) {
            console.warn(`[Wizard] Error evaluando permiso para campo ${field.name}:`, permError);
            // Continuar con el campo permitido por defecto
            fieldAllowed = true;
          }
        }

        // Usar la referencia actualizada de components
        const currentComponents = window.SitecComponents || components;
        if (!currentComponents || !currentComponents.createField) {
          console.error(`[Wizard] ❌ SitecComponents.createField no disponible al renderizar campo ${field.name}`);
          continue; // Saltar este campo
        }

        let fieldEl;
        if (!fieldAllowed) {
          // Mostrar campo como solo lectura si no tiene permiso de edición
          const readOnlyField = { ...field, readonly: true, disabled: true };
          fieldEl = currentComponents.createField(readOnlyField);
          if (fieldEl) {
            fieldEl.classList.add("field--readonly");
          }
        } else {
          fieldEl = currentComponents.createField(field);
        }

        if (!fieldEl) {
          console.error(`[Wizard] ❌ createField retornó null/undefined para campo ${field.name}`);
          continue; // Saltar este campo
        }

        if (field.type === "textarea") {
          textareas.push(fieldEl);
        } else {
          grid.appendChild(fieldEl);
        }
      } catch (fieldError) {
        console.error(`[Wizard] ❌ Error renderizando campo ${field.name}:`, fieldError);
        console.error(`[Wizard] Stack:`, fieldError.stack);
        // Continuar con el siguiente campo en lugar de detener todo el renderizado
      }
    }
    
    if (grid.children.length) panel.appendChild(grid);
    textareas.forEach((fieldEl) => panel.appendChild(fieldEl));

    container.appendChild(panel);
    console.log(`[Wizard] ✅ Sección "${section.title || `Paso ${step}`}" renderizada con ${fields.length} campos`);
  }
  
  const totalFields = container.querySelectorAll('input, select, textarea').length;
  const totalPanels = container.querySelectorAll('.wizard__panel').length;
  const visiblePanels = Array.from(container.querySelectorAll('.wizard__panel')).filter(p => p.offsetParent !== null).length;
  const visibleFields = Array.from(container.querySelectorAll('input, select, textarea')).filter(f => f.offsetParent !== null).length;
  
  console.log(`[Wizard] ✅ Renderizado del paso ${step} completado.`);
  console.log(`[Wizard] - Total de secciones renderizadas: ${totalPanels}`);
  console.log(`[Wizard] - Secciones visibles: ${visiblePanels}`);
  console.log(`[Wizard] - Total de campos en contenedor: ${totalFields}`);
  console.log(`[Wizard] - Campos visibles: ${visibleFields}`);
  console.log(`[Wizard] - Contenedor visible: ${container.offsetParent !== null}`);
  console.log(`[Wizard] - Contenedor tiene hijos: ${container.children.length > 0}`);
  console.log(`[Wizard] - Estilo display del contenedor: ${window.getComputedStyle(container).display}`);
  console.log(`[Wizard] - Estilo visibility del contenedor: ${window.getComputedStyle(container).visibility}`);
  
  // Verificar si los paneles están abiertos
  const panels = container.querySelectorAll('.wizard__panel');
  panels.forEach((panel, index) => {
    if (panel.tagName === 'DETAILS') {
      console.log(`[Wizard] - Panel ${index + 1} (details) está abierto: ${panel.open}`);
    }
  });
  
  if (totalFields === 0 && sections.length > 0) {
    console.error(`[Wizard] ⚠️ ADVERTENCIA: Se renderizaron ${sections.length} secciones pero no se encontraron campos en el DOM`);
    console.error(`[Wizard] Esto puede indicar un problema con createField o con la estructura del schema`);
  }
  
  if (visibleFields === 0 && totalFields > 0) {
    console.error(`[Wizard] ⚠️ ADVERTENCIA: Se renderizaron ${totalFields} campos pero ninguno es visible`);
    console.error(`[Wizard] Esto puede indicar un problema de CSS o de visibilidad`);
    console.error(`[Wizard] Verificando estilos de los campos...`);
    
    // Verificar estilos de los primeros campos
    const firstFields = Array.from(container.querySelectorAll('input, select, textarea')).slice(0, 3);
    firstFields.forEach((field, index) => {
      const computedStyle = window.getComputedStyle(field);
      console.error(`[Wizard] Campo ${index + 1}: display=${computedStyle.display}, visibility=${computedStyle.visibility}, opacity=${computedStyle.opacity}`);
    });
  }
}

async function enhanceWizardComponents() {
  const components = getComponents();
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

// Función helper para restaurar una firma en el canvas (mantener en pantalla)
function restoreSignature(input, value) {
  if (!input || !value || !value.startsWith("data:image")) return;

  function drawOnCanvas() {
    const signaturePad = input.closest(".signature-pad");
    if (!signaturePad) return false;
    const canvas = signaturePad.querySelector("canvas");
    if (!canvas || !canvas.isConnected) return false;

    const ctx = canvas.getContext("2d");
    const img = new Image();
    img.onload = () => {
      requestAnimationFrame(() => {
        if (!canvas.isConnected) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        const status = signaturePad.querySelector(".helper");
        const downloadBtn = Array.from(signaturePad.querySelectorAll("button")).find(
          (btn) => btn.textContent.includes("Descargar")
        );
        if (downloadBtn) downloadBtn.disabled = false;
        if (status) {
          status.textContent = "Firma cargada";
          signaturePad.dataset.state = "ready";
        }
      });
    };
    img.onerror = () => {
      console.warn("[Wizard] Error cargando imagen de firma para", input.name);
    };
    img.src = value;
    return true;
  }

  setTimeout(() => {
    if (drawOnCanvas()) return;
    setTimeout(() => {
      if (drawOnCanvas()) return;
      setTimeout(() => restoreSignature(input, value), 500);
    }, 300);
  }, 100);
}

function loadDraft() {
  const { step } = getWizardMeta();
  const store = getDraftStore();
  const payload = store.steps[step];
  if (!payload) return;
  Object.keys(payload).forEach((key) => {
    const input = document.querySelector(`[name="${key}"]`);
    if (!input) return;
    // No sobrescribir firmas ya dibujadas en pantalla (evita que se borren los trazos)
    if (key.startsWith("signature_") && input.value && input.value.startsWith("data:image")) {
      return;
    }
    input.value = payload[key];
    if (key.startsWith("signature_")) {
      restoreSignature(input, payload[key]);
    }
    input.dispatchEvent(new Event("change", { bubbles: true }));
  });
}

function setupAutosave() {
  // Guardar draft cuando cambian los campos (especialmente importante para firmas)
  document.addEventListener("change", (e) => {
    if (e.target && e.target.hasAttribute("data-autosave")) {
      // Guardar inmediatamente si es un campo de firma
      if (e.target.name && e.target.name.startsWith("signature_")) {
        saveDraft();
      }
    }
  }, true); // Usar capture phase para capturar eventos antes de que se propaguen
  
  // También guardar periódicamente
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
      headers: { 
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
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
      if (result.critical.length) {
        // Traducir códigos de error a mensajes descriptivos
        const errorMessages = result.critical.map(errorCode => {
          return ERROR_MESSAGES[errorCode] || errorCode;
        });
        critical.textContent = `Errores críticos: ${errorMessages.join(". ")}`;
      } else {
        critical.textContent = "Sin errores críticos.";
      }
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
    incidents_detail_required: "Si reportaste incidentes, debes proporcionar el detalle de los incidentes. Por favor completa el campo 'Detalle de incidentes'.",
    mitigation_plan_required: "Si la severidad del incidente es 'alta', debes proporcionar un plan de mitigación. Por favor completa el campo 'Plan de mitigación'.",
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
    console.log("[Wizard] Solicitando contraseña para re-autenticación...");
    const password = prompt("🔒 RE-AUTENTICACIÓN REQUERIDA\n\nPor seguridad, debe ingresar su contraseña para continuar al siguiente paso.\n\nIngrese su contraseña:");
    if (!password) {
      console.log("[Wizard] Re-autenticación cancelada por el usuario");
      reject(new Error("Re-autenticación cancelada"));
      return;
    }
    
    if (!password.trim()) {
      console.log("[Wizard] Contraseña vacía");
      reject(new Error("La contraseña no puede estar vacía"));
      return;
    }
    
    console.log("[Wizard] Verificando contraseña...");
    fetch("/api/wizard/verify-password/", {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      credentials: "include", // Incluir cookies de sesión
      body: JSON.stringify({ password }),
    })
      .then((response) => {
        console.log("[Wizard] Respuesta de verificación de contraseña:", response.status);
        if (response.ok) {
          return response.json();
        } else {
          // Si es 401, la contraseña es incorrecta
          if (response.status === 401) {
            return response.json().then(data => {
              console.error("[Wizard] Contraseña incorrecta:", data.error);
              throw new Error(data.error || "Contraseña incorrecta");
            });
          }
          throw new Error("Error al verificar contraseña");
        }
      })
      .then((data) => {
        if (data.verified) {
          console.log("[Wizard] ✅ Re-autenticación exitosa");
          resolve();
        } else {
          console.error("[Wizard] Verificación fallida:", data.error);
          reject(new Error(data.error || "Contraseña incorrecta"));
        }
      })
      .catch((error) => {
        console.error("[Wizard] Error en re-autenticación:", error);
        // Si el error ya tiene mensaje, usarlo; si no, usar mensaje genérico
        reject(error.message ? error : new Error("Error al verificar contraseña. Por favor intenta de nuevo."));
      });
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
    // Asegurar que resolution sea un objeto, no null
  const resolutionData = resolution || {};
  
  // Usar SyncManager con circuit breaker y reintentos
    const result = syncManager
      ? await syncManager.syncWithRetry(steps, resolutionData)
      : await fetch(API.sync, {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
          },
          credentials: "include", // Incluir cookies de sesión
          body: JSON.stringify({ steps, resolution: resolutionData }),
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
      // Solo mostrar conflictos si no hay una resolución proporcionada
      // Si hay resolución, el servidor debería haberla procesado
      if (!resolution || Object.keys(resolution).length === 0) {
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
      } else {
        // Hay resolución pero aún hay conflictos - puede ser un nuevo conflicto
        console.warn("[Wizard] Conflicto persistente después de resolución:", result.conflicts);
        showConflictBanner(result.conflicts);
        setSyncStatus("Error");
        return;
      }
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
  const { step, total } = getWizardMeta();
  const btnPrev = document.getElementById("btnPrev");
  const btnNext = document.getElementById("btnNext");
  const btnSave = document.getElementById("btnSave");
  
  console.log("[Wizard] Aplicando permisos a navegación, botones encontrados:", {
    btnPrev: !!btnPrev,
    btnNext: !!btnNext,
    btnSave: !!btnSave
  });
  
  // Evaluar permisos para navegación
  let permissions = new Map();
  if (window.permissionsManager && typeof window.permissionsManager.evaluateMultiple === 'function') {
    try {
      permissions = await window.permissionsManager.evaluateMultiple([
        "wizard.save",
        step > 1 ? `wizard.step.${step - 1}.view` : null,
        step < total ? `wizard.step.${step + 1}.view` : null,
      ].filter(Boolean));
    } catch (permError) {
      console.warn("[Wizard] Error evaluando permisos de navegación, continuando sin restricciones:", permError);
      // Continuar sin restricciones si falla la evaluación
      permissions = new Map([
        ["wizard.save", { allowed: true }],
        [step > 1 ? `wizard.step.${step - 1}.view` : null, { allowed: true }],
        [step < total ? `wizard.step.${step + 1}.view` : null, { allowed: true }]
      ].filter(([key]) => key !== null));
    }
  } else {
    console.log("[Wizard] permissionsManager no disponible, continuando sin restricciones de permisos");
    // Sin permissionsManager, permitir todo
    permissions = new Map([
      ["wizard.save", { allowed: true }],
      [step > 1 ? `wizard.step.${step - 1}.view` : null, { allowed: true }],
      [step < total ? `wizard.step.${step + 1}.view` : null, { allowed: true }]
    ].filter(([key]) => key !== null));
  }
  
  // Aplicar permisos a botones
  if (btnSave) {
    const saveAllowed = permissions.get("wizard.save")?.allowed ?? true;
    if (!saveAllowed) {
      btnSave.disabled = true;
      btnSave.title = "No tienes permisos para guardar";
      console.log("[Wizard] Botón Guardar deshabilitado por permisos");
    } else {
      btnSave.disabled = false;
    }
  }
  
  if (btnPrev && step > 1) {
    const prevStepAction = `wizard.step.${step - 1}.view`;
    const prevAllowed = permissions.get(prevStepAction)?.allowed ?? true;
    if (!prevAllowed) {
      btnPrev.disabled = true;
      btnPrev.title = "No tienes permisos para ver el paso anterior";
      console.log("[Wizard] Botón Anterior deshabilitado por permisos");
    } else {
      // No deshabilitar si tiene permisos (puede estar deshabilitado por step <= 1)
      if (step > 1) {
        btnPrev.disabled = false;
      }
    }
  }
  
  if (btnNext && step < total) {
    const nextStepAction = `wizard.step.${step + 1}.view`;
    const nextAllowed = permissions.get(nextStepAction)?.allowed ?? true;
    if (!nextAllowed) {
      btnNext.disabled = true;
      btnNext.title = "No tienes permisos para ver el siguiente paso";
      console.log("[Wizard] Botón Siguiente deshabilitado por permisos");
    } else {
      // No deshabilitar si tiene permisos (puede estar deshabilitado por step >= total)
      if (step < total) {
        btnNext.disabled = false;
      }
    }
  }
}

// Función de inicialización del wizard
async function initializeWizard() {
  console.log("[Wizard] ===== INICIANDO WIZARD =====");
  // Verificar si el usuario está autenticado antes de inicializar
  const wizardSection = document.querySelector(".wizard");
  if (!wizardSection) {
    // Usuario no autenticado, no inicializar wizard
    console.log("[Wizard] Usuario no autenticado, wizard no inicializado");
    return;
  }
  if (!document.querySelector(".wizard")) {
    console.warn("[Wizard] No se encontró el elemento .wizard");
    return;
  }
  
  console.log("[Wizard] Verificando dependencias...");
  let wizardComponents = getComponents();
  console.log("[Wizard] SitecComponents disponible (inicial):", !!wizardComponents);
  console.log("[Wizard] window.SitecComponents tipo:", typeof window.SitecComponents);
  console.log("[Wizard] window.SitecComponents valor:", window.SitecComponents);
  
  // Si no está disponible, esperar un poco más - puede ser un problema de timing
  if (!wizardComponents) {
    console.log("[Wizard] ⏳ SitecComponents no disponible inicialmente, esperando...");
    // Esperar un poco más antes de empezar a verificar
    await new Promise(resolve => setTimeout(resolve, 500));
    wizardComponents = getComponents();
    console.log("[Wizard] SitecComponents después de esperar 500ms:", !!wizardComponents);
  }
  
  // Esperar un poco si components no está disponible aún
  if (!wizardComponents) {
    console.log("[Wizard] ⏳ Esperando a que se carguen los componentes...");
    let retries = 0;
    const maxRetries = 50; // Aumentar a 50 intentos (5 segundos)
    while (!getComponents() && retries < maxRetries) {
      await new Promise(resolve => setTimeout(resolve, 100));
      retries++;
      if (retries % 10 === 0) {
        console.log(`[Wizard] Esperando SitecComponents... (intento ${retries}/${maxRetries})`);
        // Verificar si components.js se está cargando
        const componentsScript = Array.from(document.scripts).find(s => s.src && s.src.includes('components.js'));
        if (componentsScript) {
          console.log("[Wizard] components.js encontrado en DOM, esperando ejecución...");
        } else {
          console.warn("[Wizard] ⚠️ components.js no encontrado en el DOM");
        }
      }
    }
    const retryComponents = getComponents();
    if (!retryComponents) {
      console.error("[Wizard] ❌ Timeout esperando SitecComponents después de", maxRetries, "intentos");
      console.error("[Wizard] Verifica que components.js se cargue antes que wizard.js");
      
      // Verificar si hay errores en la consola
      const componentsScript = Array.from(document.scripts).find(s => s.src && s.src.includes('components.js'));
      if (!componentsScript) {
        console.error("[Wizard] ❌ components.js no está en el DOM - el lazy-loader no lo cargó");
      } else {
        console.error("[Wizard] ⚠️ components.js está en el DOM pero no se ejecutó - puede haber un error de sintaxis");
      }
      
      const container = document.getElementById("wizardDynamicContainer");
      if (container) {
        container.innerHTML = `<div class="alert alert--error">
          <strong>Error de carga</strong>
          <p>Los componentes necesarios no se cargaron. Por favor, recarga la página.</p>
          <p style="font-size: 0.875rem; margin-top: 0.5rem;">Verifica la consola del navegador para más detalles.</p>
        </div>`;
      }
      return;
    }
    console.log("[Wizard] ✅ SitecComponents cargado después de esperar");
  }
  
  setupAutosave();
  setupFieldMode();
  applyAutoFieldMode();
  setupFab();
  setupProgress();
  setSyncStatus(navigator.onLine ? "Sincronizado" : "Offline");
  
  const { step } = getWizardMeta();
  console.log("[Wizard] Paso actual:", step);

  try {
    await renderWizardStep(step);
    console.log("[Wizard] ✅ renderWizardStep completado sin errores");
  } catch (renderError) {
    console.error("[Wizard] ❌ Error en renderWizardStep:", renderError);
    console.error("[Wizard] Stack:", renderError.stack);
    const container = document.getElementById("wizardDynamicContainer");
    if (container) {
      container.innerHTML = `<div class="alert alert--error">
        <strong>Error al renderizar el formulario</strong>
        <p>Ocurrió un error al cargar los campos del wizard.</p>
        <p style="font-size: 0.875rem; margin-top: 0.5rem;">Error: ${renderError.message}</p>
        <p style="font-size: 0.875rem; margin-top: 0.5rem;">Verifica la consola del navegador para más detalles.</p>
        <p style="font-size: 0.875rem; margin-top: 0.5rem;">Intenta recargar la página (F5).</p>
      </div>`;
    }
  }
  loadDraft();
  await enhanceWizardComponents();
  // Restaurar firmas en canvas después de que los pads existan (mantener en pantalla)
  ["signature_tech", "signature_supervisor", "signature_client"].forEach((name) => {
    const input = document.querySelector(`[name="${name}"]`);
    if (input && input.value && input.value.startsWith("data:image")) {
      restoreSignature(input, input.value);
    }
  });
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
            if (!input) return;
            // No sobrescribir firmas ya dibujadas/guardadas (evita que se borren los trazos)
            if (key.startsWith("signature_") && input.value && input.value.startsWith("data:image")) {
              return;
            }
            input.value = record.data[key];
            if (key.startsWith("signature_")) {
              restoreSignature(input, record.data[key]);
            }
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
          if (!input) return;
          // No sobrescribir firmas ya dibujadas/guardadas (evita que se borren los trazos)
          if (key.startsWith("signature_") && input.value && input.value.startsWith("data:image")) {
            return;
          }
          input.value = record.data[key];
          if (key.startsWith("signature_")) {
            restoreSignature(input, record.data[key]);
          }
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
  
  const advancedComponents = getComponents();
  if (advancedComponents && advancedComponents.startAdvancedComponents) {
    const wizard = document.querySelector(".wizard");
    const projectId = wizard?.dataset?.projectId || "";
    const refreshRaw = wizard?.dataset?.refreshMs;
    const refreshMs = refreshRaw ? parseInt(refreshRaw, 10) : 60000;
    const normalizedRefresh = Number.isNaN(refreshMs) ? 60000 : refreshMs;
    advancedComponents.startAdvancedComponents(projectId, { refreshMs: normalizedRefresh });
  }

  setupPdfPanel();
  setupAiChat();

  // Configurar navegación - esperar a que el DOM esté completamente listo
  // Esperar un poco para asegurar que todos los elementos estén en el DOM
  console.log("[Wizard] Preparando para configurar navegación...");
  
  // Función para configurar navegación con múltiples intentos
  async function setupNavigationWithRetry() {
    let attempts = 0;
    const maxAttempts = 5;
    
    while (attempts < maxAttempts) {
      attempts++;
      console.log(`[Wizard] Intento ${attempts} de configurar navegación...`);
      
      try {
        await setupNavigation();
        console.log("[Wizard] ✅ Navegación configurada exitosamente");
        
        // Verificar que los listeners se agregaron
        const btnNextCheck = document.getElementById("btnNext");
        const btnPrevCheck = document.getElementById("btnPrev");
        if (btnNextCheck && btnNextCheck.onclick) {
          console.log("[Wizard] ✅ btnNext tiene onclick asignado");
        } else {
          console.warn("[Wizard] ⚠️ btnNext NO tiene onclick después de setupNavigation");
        }
        if (btnPrevCheck && btnPrevCheck.onclick) {
          console.log("[Wizard] ✅ btnPrev tiene onclick asignado");
        } else {
          console.warn("[Wizard] ⚠️ btnPrev NO tiene onclick después de setupNavigation");
        }
        
        return; // Éxito, salir
      } catch (error) {
        console.error(`[Wizard] Error en intento ${attempts}:`, error);
        if (attempts < maxAttempts) {
          await new Promise(resolve => setTimeout(resolve, 200));
        } else {
          console.error("[Wizard] ❌ Falló después de", maxAttempts, "intentos");
        }
      }
    }
  }
  
  // Ejecutar con retry
  await setupNavigationWithRetry();
  
  // Verificación y asignación directa como último recurso (múltiples intentos)
  function ensureButtonsWork() {
    const btnNextFinal = document.getElementById("btnNext");
    const btnPrevFinal = document.getElementById("btnPrev");
    
    if (!btnNextFinal || !btnPrevFinal) {
      console.warn("[Wizard] Botones aún no disponibles, reintentando...");
      return false;
    }
    
    let fixed = false;
    
    if (!btnNextFinal.onclick) {
      console.warn("[Wizard] ⚠️ CRÍTICO: btnNext no tiene onclick, asignando directamente...");
      const { step, total } = getWizardMeta();
      btnNextFinal.onclick = async function(e) {
        e?.preventDefault();
        e?.stopPropagation();
        console.log("[Wizard] ✅✅✅ Click en btnNext (asignación directa)!");
        const next = Math.min(total, step + 1);
        window.location.href = `/wizard/${next}/`;
      };
      btnNextFinal.addEventListener("click", btnNextFinal.onclick);
      console.log("[Wizard] ✅ btnNext.onclick asignado directamente:", typeof btnNextFinal.onclick);
      fixed = true;
    }
    
    if (!btnPrevFinal.onclick) {
      console.warn("[Wizard] ⚠️ CRÍTICO: btnPrev no tiene onclick, asignando directamente...");
      const { step } = getWizardMeta();
      btnPrevFinal.onclick = function(e) {
        e?.preventDefault();
        e?.stopPropagation();
        console.log("[Wizard] ✅✅✅ Click en btnPrev (asignación directa)!");
        const prev = Math.max(1, step - 1);
        window.location.href = `/wizard/${prev}/`;
      };
      btnPrevFinal.addEventListener("click", btnPrevFinal.onclick);
      console.log("[Wizard] ✅ btnPrev.onclick asignado directamente:", typeof btnPrevFinal.onclick);
      fixed = true;
    }
    
    if (fixed) {
      console.log("[Wizard] ✅✅✅ Botones corregidos con asignación directa!");
    }
    
    return btnNextFinal.onclick && btnPrevFinal.onclick;
  }
  
  // Intentar múltiples veces
  let retries = 0;
  const maxRetries = 10;
  const checkInterval = setInterval(() => {
    retries++;
    if (ensureButtonsWork() || retries >= maxRetries) {
      clearInterval(checkInterval);
      if (retries >= maxRetries) {
        console.error("[Wizard] ❌ No se pudieron asignar los listeners después de", maxRetries, "intentos");
      }
    }
  }, 200);

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
}

  // Función para inicializar con retry si SitecComponents no está disponible
  async function initializeWithRetry() {
    console.log("[Wizard] initializeWithRetry() llamado");
    // Esperar un poco para asegurar que components.js se haya ejecutado
    await new Promise(resolve => setTimeout(resolve, 200));
    
    // Verificar si SitecComponents está disponible
    console.log("[Wizard] Verificando SitecComponents...", typeof window.SitecComponents);
    if (!window.SitecComponents) {
      console.warn("[Wizard] SitecComponents no disponible, esperando hasta 3 segundos...");
      let retries = 0;
      const maxRetries = 30; // 3 segundos
      while (!window.SitecComponents && retries < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, 100));
        retries++;
        if (retries % 10 === 0) {
          console.log(`[Wizard] Esperando SitecComponents... (${retries}/${maxRetries})`);
        }
      }
      
      if (!window.SitecComponents) {
        console.error("[Wizard] ❌ SitecComponents no disponible después de esperar 3 segundos");
        console.error("[Wizard] Verificando manualmente...");
        const script = Array.from(document.scripts).find(s => s.src && s.src.includes('components.js'));
        if (script) {
          console.error("[Wizard] components.js está en el DOM pero SitecComponents no está disponible");
          console.error("[Wizard] Esto puede indicar un error en components.js");
        }
        // Aún así intentar inicializar - puede que funcione
        console.warn("[Wizard] ⚠️ Intentando inicializar sin SitecComponents...");
      } else {
        console.log("[Wizard] ✅ SitecComponents disponible después de esperar");
      }
    } else {
      console.log("[Wizard] ✅ SitecComponents disponible inmediatamente");
      console.log("[Wizard] SitecComponents.createField:", typeof window.SitecComponents.createField);
    }
    
    // Inicializar el wizard
    try {
      await initializeWizard();
      console.log("[Wizard] ✅ initializeWizard() completado");
    } catch (error) {
      console.error("[Wizard] ❌ Error en initializeWizard():", error);
      console.error("[Wizard] Stack:", error.stack);
    }
  }
  
  // Exponer función global para inicialización manual
  window.initializeWizardManually = initializeWithRetry;
  window.initializeWizardDirect = initializeWizard;
  
  // Inicializar wizard cuando el DOM esté listo o inmediatamente si ya está listo
  console.log("[Wizard] Estado del DOM:", document.readyState);
  console.log("[Wizard] __WIZARD_LOADED__:", window.__WIZARD_LOADED__);
  
  if (document.readyState === "loading") {
    console.log("[Wizard] DOM aún cargando, esperando DOMContentLoaded...");
    document.addEventListener("DOMContentLoaded", () => {
      console.log("[Wizard] DOMContentLoaded disparado, inicializando con retry...");
      initializeWithRetry();
    });
  } else {
    // DOM ya está listo, ejecutar con retry
    console.log("[Wizard] ✅ DOM ya está listo, inicializando con retry...");
    // Usar setTimeout para asegurar que otros scripts se hayan ejecutado
    setTimeout(() => {
      initializeWithRetry();
    }, 100);
  }
  
  // Función de diagnóstico para verificar por qué no se muestra el formulario
  // Verificar inmediatamente y luego después de 3 segundos
  setTimeout(() => {
    const container = document.getElementById("wizardDynamicContainer");
    const hasWizard = !!document.querySelector(".wizard");
    const hasComponents = !!window.SitecComponents;
    const hasCreateField = !!(window.SitecComponents && window.SitecComponents.createField);
    const wizardInitialized = typeof window.__WIZARD_LOADED__ !== "undefined";
    
    console.log("[Wizard] 🔍 DIAGNÓSTICO (3 segundos después de carga):");
    console.log("[Wizard] - __WIZARD_LOADED__:", wizardInitialized);
    console.log("[Wizard] - Elemento .wizard:", hasWizard);
    console.log("[Wizard] - SitecComponents disponible:", hasComponents);
    console.log("[Wizard] - createField disponible:", hasCreateField);
    console.log("[Wizard] - Contenedor existe:", !!container);
    console.log("[Wizard] - Hijos del contenedor:", container ? container.children.length : 0);
    console.log("[Wizard] - Campos en contenedor:", container ? container.querySelectorAll('input, select, textarea').length : 0);
    
    if (container && container.children.length === 0) {
      console.warn("[Wizard] ⚠️ ADVERTENCIA: El contenedor está vacío después de 3 segundos");
      
      if (!wizardInitialized) {
        console.error("[Wizard] ❌ wizard.js no se inicializó (__WIZARD_LOADED__ no está definido)");
        console.error("[Wizard] Esto indica que wizard.js no se ejecutó o falló antes de establecer el flag");
      }
      
      if (!hasComponents) {
        console.error("[Wizard] ❌ SitecComponents no está disponible");
        console.error("[Wizard] Verificando scripts cargados...");
        const scripts = Array.from(document.scripts);
        const componentsScript = scripts.find(s => s.src && s.src.includes('components.js'));
        const wizardScript = scripts.find(s => s.src && s.src.includes('wizard.js'));
        
        console.error("[Wizard] - components.js en DOM:", !!componentsScript);
        console.error("[Wizard] - wizard.js en DOM:", !!wizardScript);
        
        if (componentsScript) {
          console.error("[Wizard] ⚠️ components.js está en el DOM pero no se ejecutó correctamente");
          console.error("[Wizard] Verifica la consola para errores de sintaxis en components.js");
        } else {
          console.error("[Wizard] ❌ components.js NO está en el DOM");
          console.error("[Wizard] El lazy-loader no lo cargó o hay un problema con la carga de scripts");
        }
      }
      
      // Intentar renderizar manualmente si es posible
      if (hasWizard && hasComponents && hasCreateField && wizardInitialized) {
        console.log("[Wizard] 🔄 Intentando renderizar manualmente...");
        try {
          const { step } = getWizardMeta();
          renderWizardStep(step).catch(err => {
            console.error("[Wizard] ❌ Error al renderizar manualmente:", err);
            console.error("[Wizard] Stack:", err.stack);
          });
        } catch (err) {
          console.error("[Wizard] ❌ Error al obtener paso o renderizar:", err);
        }
      } else {
        console.warn("[Wizard] ⚠️ No se puede renderizar manualmente - faltan dependencias");
        console.warn("[Wizard] - wizard:", hasWizard, "components:", hasComponents, "createField:", hasCreateField, "initialized:", wizardInitialized);
      }
    } else if (container && container.children.length > 0) {
      console.log("[Wizard] ✅ El contenedor tiene contenido, el formulario debería estar visible");
      const fields = container.querySelectorAll('input, select, textarea');
      console.log("[Wizard] - Total de campos:", fields.length);
      console.log("[Wizard] - Campos visibles:", Array.from(fields).filter(f => f.offsetParent !== null).length);
    }
  }, 3000);

// Variable global para el flag de navegación (fuera de setupNavigation para persistir)
let globalIsNavigating = false;

async function setupNavigation() {
  console.log("[Wizard] Configurando navegación...");
  const btnPrev = document.getElementById("btnPrev");
  const btnNext = document.getElementById("btnNext");
  const btnSave = document.getElementById("btnSave");
  const { step, total } = getWizardMeta();

  console.log("[Wizard] Botones encontrados:", {
    btnPrev: !!btnPrev,
    btnNext: !!btnNext,
    btnSave: !!btnSave,
    step,
    total
  });

  // Verificar que los botones existan antes de continuar
  if (!btnPrev && !btnNext) {
    console.error("[Wizard] ERROR CRÍTICO: No se encontraron los botones de navegación");
    console.error("[Wizard] btnPrev:", btnPrev);
    console.error("[Wizard] btnNext:", btnNext);
    return;
  }

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
    console.log("[Wizard] Configurando botón Anterior...");
    btnPrev.disabled = step <= 1;
    console.log("[Wizard] Botón Anterior disabled:", btnPrev.disabled);
    
    // Función de navegación anterior
    const navigatePrev = function(e) {
      if (e) {
        e.preventDefault();
        e.stopPropagation();
      }
      console.log("[Wizard] ✅✅✅ Click en botón Anterior detectado!");
      const prev = Math.max(1, step - 1);
      console.log("[Wizard] Redirigiendo a paso:", prev);
      window.location.href = `/wizard/${prev}/`;
    };
    
    // Asignar onclick directamente
    btnPrev.onclick = navigatePrev;
    
    // También agregar addEventListener
    btnPrev.addEventListener("click", navigatePrev);
    
    console.log("[Wizard] ✅ Event listeners agregados al botón Anterior");
    console.log("[Wizard] btnPrev.onclick tipo:", typeof btnPrev.onclick);
    console.log("[Wizard] btnPrev referencia:", btnPrev);
  } else {
    console.error("[Wizard] ❌ Botón Anterior (btnPrev) no encontrado en el DOM");
  }

  if (btnNext) {
    console.log("[Wizard] Configurando botón Siguiente...");
    btnNext.disabled = step >= total;
    console.log("[Wizard] Botón Siguiente disabled:", btnNext.disabled);
    
    // Función de navegación siguiente
    let originalText = "Siguiente"; // Texto original del botón
    
    const navigateNext = async function(e) {
      if (e) {
        e.preventDefault();
        e.stopPropagation();
      }
      
      // Prevenir doble ejecución (usar variable global)
      if (globalIsNavigating) {
        console.warn("[Wizard] ⚠️ Navegación ya en progreso (globalIsNavigating=" + globalIsNavigating + "), ignorando click duplicado");
        const btnNextCheck = document.getElementById("btnNext");
        console.warn("[Wizard] 🔍 Estado del botón:", {
          disabled: btnNextCheck?.disabled,
          text: btnNextCheck?.textContent,
          exists: !!btnNextCheck,
          pointerEvents: btnNextCheck?.style.pointerEvents,
          opacity: btnNextCheck?.style.opacity
        });
        // Si el botón está deshabilitado pero el flag está en true por más de 5 segundos, resetear
        if (btnNextCheck && btnNextCheck.disabled) {
          console.warn("[Wizard] ⚠️ Botón deshabilitado detectado, forzando reset después de 2 segundos...");
          setTimeout(() => {
            if (globalIsNavigating && btnNextCheck.disabled) {
              console.warn("[Wizard] 🔄 Reset forzado por timeout");
              globalIsNavigating = false;
              btnNextCheck.disabled = false;
              btnNextCheck.textContent = originalText;
              btnNextCheck.style.pointerEvents = "auto";
              btnNextCheck.style.opacity = "1";
            }
          }, 2000);
        }
        return;
      }
      globalIsNavigating = true;
      console.log("[Wizard] ✅ Flag globalIsNavigating establecido a true");
      
      // Guardar referencia al botón y texto original
      const btnNextCurrent = document.getElementById("btnNext");
      if (btnNextCurrent) {
        originalText = btnNextCurrent.textContent || "Siguiente";
      }
      
      // Función helper para resetear el botón
      const resetButton = () => {
        console.log("[Wizard] 🔄 Reseteando botón y flag globalIsNavigating...");
        globalIsNavigating = false;
        console.log("[Wizard] ✅ globalIsNavigating reseteado a:", globalIsNavigating);
        const btnNextReset = document.getElementById("btnNext");
        if (btnNextReset) {
          btnNextReset.disabled = false;
          btnNextReset.textContent = originalText;
          // Asegurar que el botón esté completamente funcional
          btnNextReset.style.pointerEvents = "auto";
          btnNextReset.style.opacity = "1";
          console.log("[Wizard] ✅ Botón re-habilitado, texto restaurado a:", originalText);
          console.log("[Wizard] 🔍 Estado final del botón:", {
            disabled: btnNextReset.disabled,
            text: btnNextReset.textContent,
            pointerEvents: btnNextReset.style.pointerEvents,
            opacity: btnNextReset.style.opacity
          });
        } else {
          console.warn("[Wizard] ⚠️ Botón btnNext no encontrado al resetear");
        }
      };
      
      // Deshabilitar botón mientras se procesa
      if (btnNextCurrent) {
        btnNextCurrent.disabled = true;
        btnNextCurrent.textContent = "Procesando...";
        
        // Re-habilitar después de un tiempo si algo falla (timeout de seguridad)
        setTimeout(() => {
          if (globalIsNavigating) {
            console.warn("[Wizard] Timeout de seguridad: re-habilitando botón");
            resetButton();
          }
        }, 30000); // 30 segundos timeout
      }
      
      console.log("[Wizard] ✅✅✅ Click en botón Siguiente detectado!");
      
      // Evaluar permiso para avanzar al siguiente paso
      const nextStep = step + 1;
      const nextStepAction = `wizard.step.${nextStep}.view`;
      if (window.permissionsManager) {
        const nextStepPermission = await window.permissionsManager.evaluate(nextStepAction);
        if (!nextStepPermission.allowed) {
          resetButton();
          alert(`No tienes permisos para acceder al paso ${nextStep}.`);
          return;
        }
      }

      const payload = getDraftPayload();
      console.log("[Wizard] Payload obtenido:", Object.keys(payload));
      
      // Intentar sincronizar antes de validar (pero no bloquear si falla)
      try {
        await saveDraft();
        console.log("[Wizard] Draft guardado");
      } catch (saveError) {
        console.warn("[Wizard] Error al guardar draft (continuando):", saveError);
      }
      
      // Re-autenticación antes de paso 11 (firmas) o paso 12 (envío final)
      if (step === 10 || step === 11) {
        try {
          console.log("[Wizard] Iniciando re-autenticación...");
          await requireReauthentication();
          console.log("[Wizard] Re-autenticación exitosa");
        } catch (error) {
          console.error("[Wizard] Error en re-autenticación:", error);
          // Resetear flag y botón en caso de error o cancelación
          console.log("[Wizard] 🔄 Llamando resetButton() después de error/cancelación...");
          resetButton();
          console.log("[Wizard] ✅ resetButton() ejecutado, globalIsNavigating ahora es:", globalIsNavigating);
          // Si fue cancelación, no mostrar alert (el usuario ya sabe que canceló)
          if (error.message && !error.message.includes("cancelada")) {
            alert("Re-autenticación requerida. " + error.message);
            triggerCriticalFeedback("Re-autenticación fallida");
          } else {
            console.log("[Wizard] Re-autenticación cancelada por el usuario");
            console.log("[Wizard] ℹ️ Puedes hacer clic en 'Siguiente' nuevamente para reintentar");
          }
          // Verificar que el botón esté listo para el siguiente intento
          setTimeout(() => {
            const btnNextVerify = document.getElementById("btnNext");
            if (btnNextVerify) {
              console.log("[Wizard] 🔍 Verificación post-reset (1 segundo después):", {
                disabled: btnNextVerify.disabled,
                text: btnNextVerify.textContent,
                globalIsNavigating: globalIsNavigating,
                onclick: typeof btnNextVerify.onclick
              });
            }
          }, 1000);
          return;
        }
      }
      
      console.log("[Wizard] Iniciando validación del paso", step);
      const validation = await fetch(API.validate, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        credentials: "include", // Incluir cookies de sesión
        body: JSON.stringify({ step, data: payload }),
      });
      
      console.log("[Wizard] Respuesta de validación:", validation.status, validation.statusText);
      
      if (!validation.ok) {
        resetButton();
        setSyncStatus("Error");
        if (validation.status === 401 || validation.status === 403) {
          showValidationBanner(["Sesión requerida. Inicia sesión e intenta de nuevo."]);
          console.error("[Wizard] Error de autenticación:", validation.status, validation.statusText);
        } else {
          const errorText = await validation.text().catch(() => "Error desconocido");
          showValidationBanner([`Error de validación: ${errorText}`]);
          console.error("[Wizard] Error de validación:", validation.status, errorText);
        }
        updateServerValidationStatus(false);
        return;
      }
      
      const result = await validation.json();
      console.log("[Wizard] Resultado de validación:", {
        allowed: result.allowed,
        critical: result.critical,
        warnings: result.warnings
      });
      
      if (!result.allowed) {
        resetButton();
        setSyncStatus("Error");
        showValidationBanner(result.critical);
        triggerCriticalFeedback("Errores críticos detectados");
        updateServerValidationStatus(false);
        console.error("[Wizard] Validación fallida. Errores críticos:", result.critical);
        return;
      }
      
      // Finalizar analytics del paso actual
      if (wizardAnalytics) {
        wizardAnalytics.endStep(step);
      }
      
      hideValidationBanner();
      updateServerValidationStatus(true);
      const next = Math.min(total, step + 1);
      console.log("[Wizard] ✅ Validación exitosa. Redirigiendo a paso:", next);
      
      // Intentar sincronizar antes de navegar (pero no bloquear)
      try {
        await syncSteps();
        console.log("[Wizard] Sincronización completada antes de navegar");
      } catch (syncError) {
        console.warn("[Wizard] Error en sincronización (continuando navegación):", syncError);
      }
      
      // Resetear flag antes de navegar
      globalIsNavigating = false;
      
      console.log("[Wizard] Navegando a paso", next);
      window.location.href = `/wizard/${next}/`;
    };
    
    // Remover listeners previos para evitar doble ejecución
    const newBtnNext = btnNext.cloneNode(true);
    btnNext.parentNode.replaceChild(newBtnNext, btnNext);
    const btnNextClean = document.getElementById("btnNext");
    
    // Asignar solo addEventListener (más confiable que onclick)
    btnNextClean.addEventListener("click", navigateNext);
    
    // También asignar onclick como fallback
    btnNextClean.onclick = navigateNext;
    
    console.log("[Wizard] ✅ Event listeners agregados al botón Siguiente");
    console.log("[Wizard] btnNext.onclick tipo:", typeof btnNext.onclick);
    console.log("[Wizard] btnNext referencia:", btnNext);
  } else {
    console.error("[Wizard] ❌ Botón Siguiente (btnNext) no encontrado en el DOM");
  }
  
  // Verificación final
  const finalBtnPrev = document.getElementById("btnPrev");
  const finalBtnNext = document.getElementById("btnNext");
  console.log("[Wizard] Verificación final de botones:");
  console.log("[Wizard] btnPrev tiene onclick:", !!finalBtnPrev?.onclick);
  console.log("[Wizard] btnNext tiene onclick:", !!finalBtnNext?.onclick);
  
  // Si los botones no tienen onclick, intentar asignarlos directamente
  if (finalBtnPrev && !finalBtnPrev.onclick) {
    console.warn("[Wizard] ⚠️ btnPrev no tiene onclick, asignando directamente...");
    finalBtnPrev.onclick = function(e) {
      e?.preventDefault();
      e?.stopPropagation();
      console.log("[Wizard] ✅ Click en botón Anterior (fallback)!");
      const { step } = getWizardMeta();
      const prev = Math.max(1, step - 1);
      window.location.href = `/wizard/${prev}/`;
    };
    finalBtnPrev.addEventListener("click", finalBtnPrev.onclick);
  }
  
  if (finalBtnNext && !finalBtnNext.onclick) {
    console.warn("[Wizard] ⚠️ btnNext no tiene onclick, asignando directamente...");
    finalBtnNext.onclick = async function(e) {
      e?.preventDefault();
      e?.stopPropagation();
      console.log("[Wizard] ✅ Click en botón Siguiente (fallback)!");
      const { step, total } = getWizardMeta();
      const next = Math.min(total, step + 1);
      window.location.href = `/wizard/${next}/`;
    };
    finalBtnNext.addEventListener("click", finalBtnNext.onclick);
  }
  
  // Verificación final después del fallback
  console.log("[Wizard] Verificación POST-fallback:");
  console.log("[Wizard] btnPrev.onclick:", typeof finalBtnPrev?.onclick);
  console.log("[Wizard] btnNext.onclick:", typeof finalBtnNext?.onclick);
}

function showValidationBanner(errors) {
  const banner = document.getElementById("validationBanner");
  // Feedback triple en errores críticos
  triggerCriticalFeedback("Errores críticos detectados");
  if (!banner) return;
  banner.style.display = "block";
  
  // Traducir códigos de error a mensajes descriptivos usando el mismo mapa que applyFieldHints
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
    incidents_detail_required: "Si reportaste incidentes, debes proporcionar el detalle de los incidentes. Por favor completa el campo 'Detalle de incidentes'.",
    mitigation_plan_required: "Si reportaste incidentes con severidad 'alta', debes proporcionar un plan de mitigación. Por favor completa el campo 'Plan de mitigación'.",
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
  
  const errorMessages = errors.map(errorCode => {
    return messageMap[errorCode] || errorCode;
  });
  
  banner.textContent = `Errores críticos: ${errorMessages.join(". ")}`;
  banner.className = "alert alert--error";
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
    (() => { const c = getComponents(); return c && c.labelFromName ? c.labelFromName(name) : name; })();
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
      empty.textContent = "Los datos del servidor son más recientes pero no hay diferencias en los campos. Se recomienda usar la versión del servidor.";
      wrapper.appendChild(empty);
      
      // Agregar botones para seleccionar fuente completa cuando no hay detalles por campo
      const actions = document.createElement("div");
      actions.className = "conflict-actions";
      actions.style.marginTop = "1rem";
      
      const useServerBtn = document.createElement("button");
      useServerBtn.className = "btn btn--primary";
      useServerBtn.textContent = "Usar versión del servidor (Recomendado)";
      useServerBtn.setAttribute("data-step", step);
      useServerBtn.setAttribute("data-choice", "server");
      useServerBtn.addEventListener("click", async () => {
        try {
          console.log("[Wizard] Resolviendo conflicto automáticamente usando servidor");
          await syncSteps({ [step]: "server" });
          hideConflictBanner();
          setSyncStatus("Sincronizado");
          // Recargar la página para reflejar los cambios
          window.location.reload();
        } catch (error) {
          console.error("[Wizard] Error al resolver conflicto:", error);
          alert("Error al resolver el conflicto. Intenta recargar la página.");
        }
      });
      
      const useClientBtn = document.createElement("button");
      useClientBtn.className = "btn btn--ghost";
      useClientBtn.textContent = "Usar versión local";
      useClientBtn.setAttribute("data-step", step);
      useClientBtn.setAttribute("data-choice", "client");
      useClientBtn.addEventListener("click", async () => {
        try {
          console.log("[Wizard] Resolviendo conflicto usando versión local");
          await syncSteps({ [step]: "client" });
          hideConflictBanner();
          setSyncStatus("Sincronizado");
          // Recargar la página para reflejar los cambios
          window.location.reload();
        } catch (error) {
          console.error("[Wizard] Error al resolver conflicto:", error);
          alert("Error al resolver el conflicto. Intenta recargar la página.");
        }
      });
      
      actions.appendChild(useServerBtn);
      actions.appendChild(useClientBtn);
      wrapper.appendChild(actions);
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
    // Solo mostrar "Resolver por campo" si hay campos para resolver
    const mergeButtonHtml = fields.length > 0 
      ? `<button data-step="${step}" data-action="merge" class="btn btn--field">Resolver por campo</button>`
      : '';
    actions.innerHTML = `
      <button data-step="${step}" data-choice="client" class="btn btn--secondary">Usar versión local</button>
      <button data-step="${step}" data-choice="server" class="btn btn--ghost">Usar versión del servidor</button>
      ${mergeButtonHtml}
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
      console.log("[Wizard] Resolviendo conflicto del paso", step, "usando:", choice);
      try {
        await syncSteps({ [step]: choice });
        // Ocultar banner después de resolver
        hideConflictBanner();
        setSyncStatus("Sincronizado");
        console.log("[Wizard] Conflicto resuelto exitosamente");
      } catch (error) {
        console.error("[Wizard] Error al resolver conflicto:", error);
        alert("Error al resolver el conflicto: " + error.message);
      }
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
      console.log("[Wizard] Resolviendo conflicto del paso", step, "por campo con:", fields);
      try {
        await syncSteps({ [step]: { mode: "merge", fields } });
        // Ocultar banner después de resolver
        hideConflictBanner();
        setSyncStatus("Sincronizado");
        console.log("[Wizard] Conflicto resuelto exitosamente por campo");
      } catch (error) {
        console.error("[Wizard] Error al resolver conflicto por campo:", error);
        alert("Error al resolver el conflicto: " + error.message);
      }
    });
  });
}

  function hideConflictBanner() {
    const banner = document.getElementById("conflictBanner");
    if (!banner) return;
    banner.style.display = "none";
    banner.innerHTML = "";
  }
  } catch (error) {
    console.error("[Wizard] ❌ ERROR FATAL en wizard.js:", error);
    console.error("[Wizard] Error name:", error.name);
    console.error("[Wizard] Error message:", error.message);
    console.error("[Wizard] Stack trace:", error.stack);
    
    // Intentar establecer el flag de todas formas
    try {
      window.__WIZARD_LOADED__ = true;
      console.log("[Wizard] ✅ __WIZARD_LOADED__ establecido después de error");
    } catch (e) {
      console.error("[Wizard] No se pudo establecer __WIZARD_LOADED__:", e);
    }
    
    // No lanzar el error para que otros scripts puedan continuar
    // throw error;
  }
})(); // Cerrar la IIFE de protección contra carga múltiple

// Verificación final después de la IIFE
if (typeof window.__WIZARD_LOADED__ === "undefined") {
  console.error("[Wizard] ❌ CRÍTICO: wizard.js se cargó pero __WIZARD_LOADED__ no está definido");
  console.error("[Wizard] Esto indica que la IIFE no se ejecutó completamente");
  // Intentar establecer el flag manualmente
  try {
    window.__WIZARD_LOADED__ = true;
    console.warn("[Wizard] ⚠️ __WIZARD_LOADED__ establecido manualmente como fallback");
  } catch (e) {
    console.error("[Wizard] No se pudo establecer __WIZARD_LOADED__ manualmente:", e);
  }
} else {
  console.log("[Wizard] ✅ Verificación final: __WIZARD_LOADED__ =", window.__WIZARD_LOADED__);
}
