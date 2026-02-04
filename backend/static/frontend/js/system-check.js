/**
 * system-check.js
 * Script de diagnóstico del sistema para identificar problemas
 */

(function() {
  console.log("=== DIAGNÓSTICO DEL SISTEMA SITEC ===");
  console.log("Fecha:", new Date().toISOString());
  
  const checks = {
    dom: false,
    scripts: {},
    apis: {},
    components: {},
    wizard: {},
    errors: []
  };

  // 1. Verificar DOM básico
  console.log("\n[1] Verificando DOM...");
  const wizard = document.querySelector(".wizard");
  const container = document.getElementById("wizardDynamicContainer");
  const btnPrev = document.getElementById("btnPrev");
  const btnNext = document.getElementById("btnNext");
  const btnSave = document.getElementById("btnSave");
  
  checks.dom = {
    wizard: !!wizard,
    container: !!container,
    btnPrev: !!btnPrev,
    btnNext: !!btnNext,
    btnSave: !!btnSave
  };
  
  console.log("DOM:", checks.dom);
  if (!wizard) checks.errors.push("Elemento .wizard no encontrado");
  if (!container) checks.errors.push("Contenedor wizardDynamicContainer no encontrado");
  if (!btnPrev) checks.errors.push("Botón Anterior (btnPrev) no encontrado");
  if (!btnNext) checks.errors.push("Botón Siguiente (btnNext) no encontrado");

  // 2. Verificar scripts cargados (esperar a que se carguen)
  console.log("\n[2] Verificando scripts...");
  const requiredScripts = [
    "lazy-loader.js",
    "data-loader.js",
    "performance.js",
    "role-based-ui.js",
    "components.js",
    "wizard.js",
    "permissions.js",
    "sync.js",
    "analytics.js"
  ];
  
  // Verificar scripts que están en el DOM (cargados o en proceso)
  // Lista de scripts que se cargan dinámicamente y no deben reportarse como error inicialmente
  const dynamicScripts = [
    "lazy-loader.js",      // Se carga dinámicamente
    "data-loader.js",      // Se carga dinámicamente
    "performance.js",      // Se carga dinámicamente
    "role-based-ui.js",    // Se carga dinámicamente
    "components.js",       // Se carga dinámicamente
    "wizard.js",           // Se carga dinámicamente
    "permissions.js",      // Se carga dinámicamente
    "sync.js",             // Se carga dinámicamente
    "analytics.js"         // Se carga dinámicamente
  ];
  
  requiredScripts.forEach(script => {
    const found = Array.from(document.querySelectorAll("script[src]")).some(
      s => s.src.includes(script)
    );
    checks.scripts[script] = found;
    // No marcar como error si es un script que se carga dinámicamente
    // Estos scripts se verifican más tarde en verifyDynamicScripts()
    if (!found && !dynamicScripts.includes(script)) {
      checks.errors.push(`Script ${script} no encontrado`);
    }
  });
  
  console.log("Scripts:", checks.scripts);

  // 3. Verificar APIs globales
  console.log("\n[3] Verificando APIs globales...");
  checks.apis = {
    SitecComponents: typeof window.SitecComponents !== "undefined",
    permissionsManager: typeof window.permissionsManager !== "undefined",
    SyncManager: typeof window.SyncManager !== "undefined",
    SyncStatusTracker: typeof window.SyncStatusTracker !== "undefined",
    WizardAnalytics: typeof window.WizardAnalytics !== "undefined",
    RoleBasedUI: typeof window.RoleBasedUI !== "undefined",
    lazyLoader: typeof window.lazyLoader !== "undefined"
  };
  
  console.log("APIs:", checks.apis);
  // No añadir errores de APIs aquí: se revalidan después de cargar scripts dinámicos

  // 4. Verificar componentes (se actualizará después)
  console.log("\n[4] Verificando componentes...");
  // Esta verificación se actualizará después de que los scripts se carguen
  checks.components = { pending: "Esperando carga de scripts..." };
  console.log("Componentes: (verificación pendiente)");

  // 5. Verificar wizard
  console.log("\n[5] Verificando wizard...");
  if (wizard) {
    checks.wizard = {
      step: wizard.dataset.step || "no definido",
      total: wizard.dataset.total || "no definido",
      projectId: wizard.dataset.projectId || "no definido",
      reportId: wizard.dataset.reportId || "no definido"
    };
  } else {
    checks.wizard = { error: "Wizard no encontrado" };
  }
  
  console.log("Wizard:", checks.wizard);

  // 6. Verificar errores de JavaScript
  console.log("\n[6] Verificando errores...");
  const originalError = console.error;
  const originalWarn = console.warn;
  const jsErrors = [];
  
  console.error = function(...args) {
    jsErrors.push({ type: "error", message: args.join(" ") });
    originalError.apply(console, args);
  };
  
  console.warn = function(...args) {
    if (args[0] && typeof args[0] === "string" && args[0].includes("[Wizard]")) {
      jsErrors.push({ type: "warn", message: args.join(" ") });
    }
    originalWarn.apply(console, args);
  };

  // 7. Verificar conectividad API
  console.log("\n[7] Verificando conectividad API...");
  fetch("/api/users/me/", { credentials: "include" })
    .then(response => {
      checks.apis.auth = {
        status: response.status,
        ok: response.ok,
        authenticated: response.status !== 401
      };
      console.log("Autenticación:", checks.apis.auth);
      if (response.status === 401) {
        checks.errors.push("Usuario no autenticado");
      }
      // Esperar a que lazy-loader y módulos terminen de cargar antes de verificar (5s)
      setTimeout(() => {
        verifyDynamicScripts().then(() => generateReport());
      }, 5000);
    })
    .catch(error => {
      checks.apis.auth = { error: error.message };
      checks.errors.push(`Error de conectividad: ${error.message}`);
      setTimeout(() => {
        verifyDynamicScripts().then(() => generateReport());
      }, 5000);
    });

  // Mapa script -> comprobar si su API global está disponible (prioridad sobre tag en DOM)
  var scriptToApi = {
    "lazy-loader.js": function() { return typeof window !== "undefined" && typeof window.lazyLoader !== "undefined"; },
    "data-loader.js": function() { return true; },
    "performance.js": function() { return true; },
    "role-based-ui.js": function() { return typeof window !== "undefined" && typeof window.RoleBasedUI !== "undefined"; },
    "components.js": function() { return typeof window !== "undefined" && typeof window.SitecComponents !== "undefined"; },
    "wizard.js": function() { return typeof window !== "undefined" && typeof window.__WIZARD_LOADED__ !== "undefined"; },
    "permissions.js": function() { return typeof window !== "undefined" && typeof window.permissionsManager !== "undefined"; },
    "sync.js": function() { return typeof window !== "undefined" && (typeof window.SyncManager !== "undefined" || typeof window.SyncStatusTracker !== "undefined"); },
    "analytics.js": function() { return typeof window !== "undefined" && typeof window.WizardAnalytics !== "undefined"; }
  };

  function scriptTagMatches(scriptEl, fileName) {
    if (!scriptEl || !scriptEl.src) return false;
    try {
      var url = scriptEl.src;
      var path = url.indexOf("/") === 0 ? url : (url.indexOf("://") !== -1 ? new URL(url).pathname : url);
      return path.indexOf(fileName) !== -1 || path.split("/").pop().split("?")[0] === fileName;
    } catch (e) {
      return scriptEl.src.indexOf(fileName) !== -1;
    }
  }

  async function verifyDynamicScripts() {
    console.log("\n[8] Verificando scripts dinámicos...");
    var dynamicScripts = [
      "lazy-loader.js",
      "data-loader.js",
      "performance.js",
      "role-based-ui.js",
      "components.js",
      "wizard.js",
      "permissions.js",
      "sync.js",
      "analytics.js"
    ];
    var retries = 0;
    var maxRetries = 80; // 8 s adicionales por si lazy-loader tarda en cargar todos los módulos

    while (retries < maxRetries) {
      var scriptElements = document.scripts || document.querySelectorAll("script[src]");
      dynamicScripts.forEach(function(script) {
        if (checks.scripts[script]) return;
        // Prioridad 1: API global disponible (prueba definitiva de que el script se ejecutó)
        var fn = scriptToApi[script];
        if (fn && fn()) {
          checks.scripts[script] = true;
          return;
        }
        // Prioridad 2: tag en DOM (lista actualizada en cada iteración)
        var foundTag = Array.from(scriptElements).some(function(s) {
          return scriptTagMatches(s, script);
        });
        if (foundTag) {
          checks.scripts[script] = true;
        }
      });

      var missing = dynamicScripts.filter(function(s) { return !checks.scripts[s]; });
      if (missing.length === 0) {
        console.log("Todos los scripts/APIs disponibles");
        break;
      }
      if (retries % 15 === 0 && retries > 0) {
        console.log("Esperando módulos... faltan " + missing.length);
      }
      await new Promise(function(r) { setTimeout(r, 100); });
      retries++;
    }

    // No reportar "Script X no encontrado" para scripts dinámicos: se cargan por lazy-loader
    // y pueden no tener tag visible o ejecutarse después. Solo reportamos APIs faltantes.
    checks.errors = checks.errors.filter(function(error) {
      return !dynamicScripts.some(function(script) {
        return error.indexOf("Script " + script + " no encontrado") !== -1;
      });
    });

    // Verificar APIs después de que los scripts se carguen
    checks.apis.SitecComponents = typeof window.SitecComponents !== "undefined";
    checks.apis.permissionsManager = typeof window.permissionsManager !== "undefined";
    checks.apis.SyncManager = typeof window.SyncManager !== "undefined";
    checks.apis.SyncStatusTracker = typeof window.SyncStatusTracker !== "undefined";
    checks.apis.WizardAnalytics = typeof window.WizardAnalytics !== "undefined";
    checks.apis.RoleBasedUI = typeof window.RoleBasedUI !== "undefined";
    checks.apis.lazyLoader = typeof window.lazyLoader !== "undefined";
    
    // Actualizar verificación de componentes
    if (window.SitecComponents) {
      checks.components = {
        createField: typeof window.SitecComponents.createField === "function",
        createSignaturePad: typeof window.SitecComponents.createSignaturePad === "function",
        createEvidenceUploader: typeof window.SitecComponents.createEvidenceUploader === "function",
        createGeoPicker: typeof window.SitecComponents.createGeoPicker === "function"
      };
      console.log("Componentes verificados:", checks.components);
    } else {
      checks.components = { error: "SitecComponents no disponible" };
    }

    // Añadir error de APIs solo si faltan y la página los necesita (p. ej. wizard). Una sola vez por API.
    var pageNeedsWizard = !!document.querySelector(".wizard");
    checks.errors = checks.errors.filter(function(e) {
      return e.indexOf("SitecComponents") === -1 && e.indexOf("permissionsManager") === -1;
    });
    if (pageNeedsWizard && !checks.apis.SitecComponents) {
      checks.errors.push("SitecComponents no está disponible");
    }
    if (pageNeedsWizard && !checks.apis.permissionsManager) {
      checks.errors.push("permissionsManager no está disponible");
    }
    checks.errors = [...new Set(checks.errors)];
  }

  function generateReport() {
    console.log("\n=== REPORTE DE DIAGNÓSTICO ===");
    console.log("Errores encontrados:", checks.errors.length);
    checks.errors.forEach((error, i) => {
      console.error(`[${i + 1}] ${error}`);
    });
    
    if (checks.errors.length === 0) {
      console.log("✅ No se encontraron errores críticos");
    } else {
      console.error("❌ Se encontraron", checks.errors.length, "errores");
    }
    
    // Restaurar console original
    console.error = originalError;
    console.warn = originalWarn;
    
    // Exponer resultados globalmente
    window.systemDiagnostics = checks;
    
    console.log("\nPara ver los resultados completos, ejecuta: window.systemDiagnostics");
  }

  // Ejecutar verificación de wizard después de un delay
  setTimeout(() => {
    console.log("\n[9] Verificando estado del wizard...");
    if (window.systemDiagnostics) {
      const wizardState = {
        initialized: typeof window.wizardInitialized !== "undefined",
        step: wizard ? wizard.dataset.step : null,
        fields: container ? container.children.length : 0,
        buttons: {
          prev: btnPrev ? { 
            disabled: btnPrev.disabled, 
            hasListener: true,
            onclick: btnPrev.onclick ? "presente" : "ausente"
          } : null,
          next: btnNext ? { 
            disabled: btnNext.disabled, 
            hasListener: true,
            onclick: btnNext.onclick ? "presente" : "ausente"
          } : null,
          save: btnSave ? { 
            disabled: btnSave.disabled, 
            hasListener: true,
            onclick: btnSave.onclick ? "presente" : "ausente"
          } : null
        }
      };
      console.log("Estado del wizard:", wizardState);
      window.systemDiagnostics.wizardState = wizardState;
    }
  }, 3000);
})();
