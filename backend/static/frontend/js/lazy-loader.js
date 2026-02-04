/**
 * lazy-loader.js
 * Sistema de carga diferida (lazy loading) para componentes JavaScript.
 * Carga solo los scripts necesarios según la página actual.
 */

// Log inmediato FORZADO - debe aparecer siempre
if (typeof console !== "undefined") {
  console.log("%c[LazyLoader] ⚡ lazy-loader.js cargado", "color: purple; font-weight: bold; font-size: 14px;");
  console.log("[LazyLoader] Timestamp:", new Date().toISOString());
  console.log("[LazyLoader] URL:", window.location.href);
  console.log("[LazyLoader] Pathname:", window.location.pathname);
} else {
  // Fallback si console no está disponible
  alert("LazyLoader: console no disponible");
}

class LazyLoader {
  constructor() {
    this.loadedModules = new Set();
    this.loadingPromises = new Map();
  }

  /**
   * Verifica si un script ya está cargado en el DOM.
   * @param {string} modulePath - Ruta del módulo
   * @returns {boolean}
   */
  isScriptAlreadyLoaded(modulePath) {
    // Para scripts críticos, verificar flags primero
    const basePath = modulePath.split("?")[0];
    const scriptName = basePath.split("/").pop();
    
    if (scriptName === "wizard.js" && window.__WIZARD_LOADED__) {
      console.log("[LazyLoader] wizard.js ya está cargado (flag __WIZARD_LOADED__ detectado)");
      return true;
    }
    if (scriptName === "components.js" && window.SitecComponents) {
      console.log("[LazyLoader] components.js ya está cargado (SitecComponents detectado)");
      return true;
    }
    
    // Verificar si está en la lista de módulos cargados (usar basePath para comparar)
    for (const loaded of this.loadedModules) {
      if (loaded === modulePath || loaded === basePath || loaded.includes(scriptName)) {
        console.log("[LazyLoader] isScriptAlreadyLoaded:", modulePath, "- en loadedModules como:", loaded);
        return true;
      }
    }
    
    // Verificar si ya existe un script con esta src (comparar basePath)
    const allScripts = Array.from(document.querySelectorAll("script[src]"));
    const existingScript = allScripts.find(s => {
      if (!s.src) return false;
      const scriptBasePath = s.src.split("?")[0];
      return scriptBasePath === basePath || scriptBasePath.includes(scriptName);
    });
    if (existingScript) {
      console.log("[LazyLoader] isScriptAlreadyLoaded:", modulePath, "- encontrado en DOM:", existingScript.src);
      return true;
    }
    
    return false;
  }

  /**
   * Carga un módulo JavaScript de forma asíncrona.
   * @param {string} modulePath - Ruta del módulo a cargar
   * @returns {Promise<void>}
   */
  async loadModule(modulePath) {
    // Para scripts críticos, SIEMPRE remover y recargar para evitar caché
    const isCriticalScript = modulePath.includes("components.js") || modulePath.includes("wizard.js");
    if (isCriticalScript) {
      const existingScript = Array.from(document.scripts).find(s => 
        s.src && (s.src === modulePath || s.src.includes(modulePath.split("/").pop()) || s.src.includes(modulePath.split("/").pop().split("?")[0]))
      );
      if (existingScript) {
        console.warn("[LazyLoader] ⚠️ Script crítico encontrado en DOM, removiendo para recargar sin caché...");
        console.warn("[LazyLoader] Script actual - async:", existingScript.async, "defer:", existingScript.defer, "src:", existingScript.src);
        // Remover el script existente
        existingScript.remove();
        // Limpiar de loadedModules para forzar recarga
        this.loadedModules.delete(modulePath);
        // También limpiar cualquier versión con parámetros
        const basePath = modulePath.split("?")[0];
        this.loadedModules.forEach(loaded => {
          if (loaded.includes(basePath)) {
            this.loadedModules.delete(loaded);
          }
        });
      }
    }
    
    // Si ya está cargado en el DOM (y no tiene async/defer si es crítico), retornar inmediatamente
    if (this.isScriptAlreadyLoaded(modulePath)) {
      // Verificar si es crítico y está correctamente configurado
      if (isCriticalScript) {
        const existingScript = Array.from(document.scripts).find(s => 
          s.src && (s.src === modulePath || s.src.includes(modulePath.split("/").pop()))
        );
        if (existingScript && !existingScript.async && !existingScript.defer) {
          console.log("[LazyLoader] Script crítico ya cargado correctamente (sin async/defer)");
          this.loadedModules.add(modulePath);
          return Promise.resolve();
        }
      } else {
        this.loadedModules.add(modulePath);
        return Promise.resolve();
      }
    }

    // Si ya está en proceso de carga, retornar la promesa existente
    if (this.loadingPromises.has(modulePath)) {
      console.log("[LazyLoader] Módulo ya en proceso de carga:", modulePath);
      return this.loadingPromises.get(modulePath);
    }

    // Verificar si ya está cargado antes de intentar cargarlo
    if (this.isScriptAlreadyLoaded(modulePath)) {
      console.log("[LazyLoader] Módulo ya cargado, omitiendo:", modulePath);
      this.loadedModules.add(modulePath);
      return Promise.resolve();
    }

    // Crear nueva promesa de carga
    const loadPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      
      // Para scripts críticos, agregar timestamp para evitar caché
      const isCriticalScript = modulePath.includes("components.js") || modulePath.includes("wizard.js");
      if (isCriticalScript) {
        // Agregar timestamp para forzar recarga y evitar caché
        const separator = modulePath.includes("?") ? "&" : "?";
        script.src = modulePath + separator + "_t=" + Date.now();
        console.log("[LazyLoader] Cargando script crítico con timestamp para evitar caché:", script.src);
      } else {
        script.src = modulePath;
      }
      
      // Para scripts críticos como components.js y wizard.js, NO usar async/defer
      // Esto asegura que se ejecuten inmediatamente después de cargarse
      if (isCriticalScript) {
        // NO establecer async ni defer - ejecución inmediata
        script.async = false;
        script.defer = false;
        console.log("%c[LazyLoader] Cargando script crítico SIN async/defer:", "color: red; font-weight: bold;", script.src);
      } else {
        script.async = true;
        script.defer = true;
        console.log("[LazyLoader] Cargando script normal con async/defer:", script.src);
      }
      
      // Verificar que los atributos se establecieron correctamente ANTES de agregar al DOM
      console.log("[LazyLoader] Script configurado ANTES de agregar - async:", script.async, "defer:", script.defer, "src:", modulePath);
      
      // Agregar al DOM ANTES de definir onload para asegurar que los atributos se mantengan
      document.head.appendChild(script);
      console.log("[LazyLoader] Script agregado al DOM");
      
      // Verificar DESPUÉS de agregar al DOM
      console.log("[LazyLoader] Script DESPUÉS de agregar - async:", script.async, "defer:", script.defer);
      
      script.onload = () => {
        // Usar la ruta original (sin timestamp) para el tracking
        const originalPath = modulePath.split("?")[0];
        this.loadedModules.add(originalPath);
        this.loadingPromises.delete(modulePath);
        console.log("%c[LazyLoader] ✅ Módulo cargado:", "color: green; font-weight: bold;", script.src);
        console.log("[LazyLoader] Script async después de onload:", script.async, "defer:", script.defer);
        
        // Para scripts críticos, verificar inmediatamente si se ejecutaron
        if (isCriticalScript) {
          // Esperar un momento para que el script se ejecute
          setTimeout(() => {
            if (modulePath.includes("components.js")) {
              console.log("[LazyLoader] 🔍 Verificando components.js después de onload...");
              console.log("[LazyLoader] SitecComponents disponible:", typeof window.SitecComponents);
              if (!window.SitecComponents) {
                console.error("[LazyLoader] ❌ components.js se cargó pero SitecComponents no está disponible");
              } else {
                console.log("[LazyLoader] ✅ components.js ejecutado correctamente");
              }
            }
            if (modulePath.includes("wizard.js")) {
              console.log("[LazyLoader] 🔍 Verificando wizard.js después de onload...");
              console.log("[LazyLoader] __WIZARD_LOADED__:", window.__WIZARD_LOADED__);
              if (!window.__WIZARD_LOADED__) {
                console.error("[LazyLoader] ❌ wizard.js se cargó pero __WIZARD_LOADED__ no está definido");
              } else {
                console.log("[LazyLoader] ✅ wizard.js ejecutado correctamente");
              }
            }
          }, 100);
        }
        
        // Para scripts críticos, verificar inmediatamente después de onload
        if (modulePath.includes("components.js")) {
          // Verificar inmediatamente
          console.log("[LazyLoader] 🔍 Verificando components.js inmediatamente después de onload...");
          console.log("[LazyLoader] window.SitecComponents (inmediato):", typeof window.SitecComponents);
          
          // También verificar después de un delay
          setTimeout(() => {
            console.log("[LazyLoader] 🔍 Verificando components.js después de 500ms...");
            console.log("[LazyLoader] window.SitecComponents (500ms):", typeof window.SitecComponents);
            
            if (!window.SitecComponents) {
              console.error("[LazyLoader] ⚠️ components.js se cargó pero no se ejecutó (SitecComponents no está definido)");
              console.error("[LazyLoader] Verifica la consola para errores de sintaxis en components.js");
              
              // Verificar si hay errores en el script
              const scriptElement = Array.from(document.scripts).find(s => s.src && s.src.includes('components.js'));
              if (scriptElement) {
                console.error("[LazyLoader] Script components.js está en el DOM pero no se ejecutó");
                console.error("[LazyLoader] URL del script:", scriptElement.src);
                console.error("[LazyLoader] Script async:", scriptElement.async, "defer:", scriptElement.defer);
                console.error("[LazyLoader] Script onerror:", scriptElement.onerror);
                
                // Intentar ejecutar el script manualmente para ver si hay errores
                console.warn("[LazyLoader] Intentando verificar si el script tiene errores...");
                try {
                  // Verificar si el contenido del script se puede acceder
                  fetch(scriptElement.src)
                    .then(response => response.text())
                    .then(text => {
                      console.log("[LazyLoader] Script descargado, longitud:", text.length);
                      // Verificar si tiene el log inicial
                      if (text.includes("[Components] ⚡ components.js cargado - INICIO")) {
                        console.warn("[LazyLoader] ⚠️ El script contiene los logs pero no se ejecutó");
                      } else {
                        console.error("[LazyLoader] ❌ El script no contiene los logs esperados - puede ser una versión antigua en caché");
                      }
                    })
                    .catch(err => console.error("[LazyLoader] Error al verificar script:", err));
                } catch (e) {
                  console.error("[LazyLoader] Error al verificar script:", e);
                }
              } else {
                console.error("[LazyLoader] ❌ components.js NO está en el DOM");
              }
              
              // Verificar si hay mensajes de [Components] en la consola
              console.warn("[LazyLoader] Si no ves mensajes [Components] en la consola, el script no se ejecutó");
            } else {
              console.log("[LazyLoader] ✅ components.js se ejecutó correctamente (SitecComponents disponible)");
              console.log("[LazyLoader] createField disponible:", typeof window.SitecComponents.createField === "function");
            }
          }, 500);
          
          // Verificar también después de más tiempo
          setTimeout(() => {
            if (!window.SitecComponents) {
              console.error("[LazyLoader] ❌ components.js aún no disponible después de 2 segundos");
            }
          }, 2000);
        }
        
        // Verificar si wizard.js se ejecutó correctamente
        if (modulePath.includes("wizard.js")) {
          // Verificar inmediatamente
          console.log("[LazyLoader] 🔍 Verificando wizard.js inmediatamente después de onload...");
          console.log("[LazyLoader] window.__WIZARD_LOADED__ (inmediato):", window.__WIZARD_LOADED__);
          
          // También verificar después de un delay
          setTimeout(() => {
            console.log("[LazyLoader] 🔍 Verificando wizard.js después de 500ms...");
            console.log("[LazyLoader] window.__WIZARD_LOADED__ (500ms):", window.__WIZARD_LOADED__);
            
            if (!window.__WIZARD_LOADED__) {
              console.error("[LazyLoader] ⚠️ wizard.js se cargó pero no se ejecutó (__WIZARD_LOADED__ no está definido)");
              console.error("[LazyLoader] Verifica la consola para errores de sintaxis en wizard.js");
              
              // Verificar si hay errores en el script
              const scriptElement = Array.from(document.scripts).find(s => s.src && s.src.includes('wizard.js'));
              if (scriptElement) {
                console.error("[LazyLoader] Script wizard.js está en el DOM pero no se ejecutó");
                console.error("[LazyLoader] URL del script:", scriptElement.src);
                console.error("[LazyLoader] Script async:", scriptElement.async, "defer:", scriptElement.defer);
                
                // Intentar verificar si el script tiene errores
                console.warn("[LazyLoader] Intentando verificar si el script tiene errores...");
                try {
                  fetch(scriptElement.src)
                    .then(response => response.text())
                    .then(text => {
                      console.log("[LazyLoader] Script descargado, longitud:", text.length);
                      // Verificar si tiene el log inicial
                      if (text.includes("[Wizard] ⚡ wizard.js cargado - INICIO")) {
                        console.warn("[LazyLoader] ⚠️ El script contiene los logs pero no se ejecutó");
                      } else {
                        console.error("[LazyLoader] ❌ El script no contiene los logs esperados - puede ser una versión antigua en caché");
                      }
                    })
                    .catch(err => console.error("[LazyLoader] Error al verificar script:", err));
                } catch (e) {
                  console.error("[LazyLoader] Error al verificar script:", e);
                }
              } else {
                console.error("[LazyLoader] ❌ wizard.js NO está en el DOM");
              }
              
              // Verificar si hay mensajes de [Wizard] en la consola
              console.warn("[LazyLoader] Si no ves mensajes [Wizard] en la consola, el script no se ejecutó");
            } else {
              console.log("[LazyLoader] ✅ wizard.js se ejecutó correctamente (__WIZARD_LOADED__ = true)");
            }
          }, 500);
          
          // Verificar también después de más tiempo
          setTimeout(() => {
            if (!window.__WIZARD_LOADED__) {
              console.error("[LazyLoader] ❌ wizard.js aún no ejecutado después de 2 segundos");
            }
          }, 2000);
        }
        
        resolve();
      };
      
      script.onerror = (error) => {
        this.loadingPromises.delete(modulePath);
        console.error("%c[LazyLoader] ❌ Error cargando módulo:", "color: red; font-weight: bold;", modulePath);
        console.error("[LazyLoader] Error details:", error);
        console.error("[LazyLoader] Script src:", script.src);
        console.error("[LazyLoader] Script async:", script.async, "defer:", script.defer);
        reject(new Error(`Failed to load module: ${modulePath}`));
      };
    });

    this.loadingPromises.set(modulePath, loadPromise);
    return loadPromise;
  }

  /**
   * Carga múltiples módulos en paralelo, pero respetando dependencias críticas.
   * components.js debe cargarse antes que wizard.js
   * @param {string[]} modulePaths - Array de rutas de módulos
   * @returns {Promise<void[]>}
   */
  async loadModules(modulePaths) {
    // Separar components.js y wizard.js para cargar components primero
    const componentsIndex = modulePaths.indexOf("/static/frontend/js/components.js");
    const wizardIndex = modulePaths.indexOf("/static/frontend/js/wizard.js");
    
    if (componentsIndex !== -1 && wizardIndex !== -1 && componentsIndex > wizardIndex) {
      // Si wizard.js está antes que components.js, reordenar
      const otherModules = modulePaths.filter((p, i) => i !== componentsIndex && i !== wizardIndex);
      // Cargar components primero, luego wizard, luego el resto
      await this.loadModule("/static/frontend/js/components.js");
      await this.loadModule("/static/frontend/js/wizard.js");
      return Promise.all(otherModules.map(path => this.loadModule(path)));
    }
    
    // Cargar en paralelo si el orden es correcto
    return Promise.all(modulePaths.map(path => this.loadModule(path)));
  }

  /**
   * Determina qué módulos cargar según la página actual.
   * Solo carga módulos que no están ya incluidos en el template.
   * @returns {string[]} Array de rutas de módulos a cargar
   */
  getModulesForCurrentPage() {
    const path = window.location.pathname;
    const modules = [];
    
    // Logs de diagnóstico FORZADOS - siempre deben aparecer
    console.log("%c[LazyLoader] getModulesForCurrentPage() - Ruta detectada:", "color: orange; font-weight: bold;", path);
    console.log("[LazyLoader] path === '/':", path === "/");
    console.log("[LazyLoader] path.startsWith('/wizard'):", path.startsWith("/wizard"));
    console.log("[LazyLoader] URL completa:", window.location.href);

    // Módulos base siempre necesarios (si no están ya cargados)
    const baseModules = [
      "/static/frontend/js/performance.js",
      "/static/frontend/js/data-loader.js",
      "/static/frontend/js/loading-states.js",
      "/static/frontend/js/role-based-ui.js",
    ];

    baseModules.forEach(module => {
      const alreadyLoaded = this.isScriptAlreadyLoaded(module);
      console.log("[LazyLoader] Verificando", module, "- ya cargado:", alreadyLoaded);
      if (!alreadyLoaded) {
        modules.push(module);
      }
    });

    // Módulos según ruta (solo si no están ya en el template)
    if (path.startsWith("/dashboard")) {
      if (!this.isScriptAlreadyLoaded("/static/frontend/js/navigation.js")) {
        modules.push("/static/frontend/js/navigation.js");
      }
      // dashboard.js y dashboard-lite.js se cargan en los templates específicos
    } else if (path === "/" || path.startsWith("/wizard")) {
      console.log("%c[LazyLoader] ✅ Ruta del wizard detectada, agregando módulos del wizard...", "color: green; font-weight: bold;");
      // La ruta raíz "/" también muestra el wizard
      // IMPORTANTE: components.js debe cargarse ANTES que wizard.js
      const wizardModules = [
        "/static/frontend/js/pwa.js",
        "/static/frontend/js/sync.js",
        "/static/frontend/js/analytics.js",
        "/static/frontend/js/permissions.js",
        "/static/frontend/js/components.js", // Debe estar antes de wizard.js
        "/static/frontend/js/wizard.js",
      ];
      wizardModules.forEach(module => {
        const alreadyLoaded = this.isScriptAlreadyLoaded(module);
        console.log("[LazyLoader] Verificando módulo wizard", module, "- ya cargado:", alreadyLoaded);
        if (!alreadyLoaded) {
          modules.push(module);
          console.log("[LazyLoader] ✅ Agregado a la lista:", module);
        } else {
          console.log("[LazyLoader] ⚠️ Omitido (ya cargado):", module);
        }
      });
      console.log("[LazyLoader] Total módulos wizard agregados:", modules.length);
    } else if (path.startsWith("/projects")) {
      if (!this.isScriptAlreadyLoaded("/static/frontend/js/navigation.js")) {
        modules.push("/static/frontend/js/navigation.js");
      }
      // sections-projects.js se carga en el template
    } else if (path.startsWith("/reports")) {
      if (!this.isScriptAlreadyLoaded("/static/frontend/js/navigation.js")) {
        modules.push("/static/frontend/js/navigation.js");
      }
      // sections-reports.js y sections-approvals.js se cargan en los templates
    } else if (path.startsWith("/documents")) {
      if (!this.isScriptAlreadyLoaded("/static/frontend/js/navigation.js")) {
        modules.push("/static/frontend/js/navigation.js");
      }
      // sections-documents.js se carga en el template
    } else {
      // Página desconocida, cargar navegación por defecto
      if (!this.isScriptAlreadyLoaded("/static/frontend/js/navigation.js")) {
        modules.push("/static/frontend/js/navigation.js");
      }
    }

    console.log("[LazyLoader] Módulos finales a cargar:", modules);
    console.log("[LazyLoader] components.js incluido:", modules.includes("/static/frontend/js/components.js"));
    console.log("[LazyLoader] wizard.js incluido:", modules.includes("/static/frontend/js/wizard.js"));
    return modules;
  }

  /**
   * Inicializa la carga diferida según la página actual.
   */
  async initialize() {
    console.log("[LazyLoader] ===== INICIANDO CARGA DE MÓDULOS =====");
    const modules = this.getModulesForCurrentPage();
    console.log("[LazyLoader] Módulos a cargar:", modules);
    console.log("[LazyLoader] Ruta actual:", window.location.pathname);
    
    try {
      // Asegurar que components.js se cargue antes que wizard.js
      const componentsIndex = modules.indexOf("/static/frontend/js/components.js");
      const wizardIndex = modules.indexOf("/static/frontend/js/wizard.js");
      
      console.log("[LazyLoader] components.js en lista:", componentsIndex !== -1);
      console.log("[LazyLoader] wizard.js en lista:", wizardIndex !== -1);
      console.log("[LazyLoader] Total módulos:", modules.length);
      console.log("[LazyLoader] Lista completa:", modules);
      
      if (componentsIndex !== -1 && wizardIndex !== -1) {
        // Cargar components.js primero
        console.log("%c[LazyLoader] 🔄 Cargando components.js primero...", "color: orange; font-weight: bold;");
        try {
          await this.loadModule("/static/frontend/js/components.js");
          console.log("[LazyLoader] ⏳ Esperando ejecución de components.js...");
          // Verificar que se ejecutó - esperar más tiempo
          await new Promise(resolve => setTimeout(resolve, 1000));
          
          // Verificar múltiples veces
          let checkCount = 0;
          while (!window.SitecComponents && checkCount < 5) {
            await new Promise(resolve => setTimeout(resolve, 200));
            checkCount++;
          }
          
          if (!window.SitecComponents) {
            console.error("[LazyLoader] ❌ components.js se cargó pero SitecComponents no está disponible después de 2 segundos");
            console.error("[LazyLoader] Verifica la consola para errores en components.js");
            
            // Verificar si el script está en el DOM
            const scriptElement = Array.from(document.scripts).find(s => 
              s.src && (s.src.includes('components.js') || s.src.endsWith('/components.js'))
            );
            if (scriptElement) {
              console.error("[LazyLoader] Script encontrado en DOM:", scriptElement.src);
              console.error("[LazyLoader] Script async:", scriptElement.async, "defer:", scriptElement.defer);
            } else {
              console.error("[LazyLoader] ❌ components.js NO está en el DOM");
            }
          } else {
            console.log("[LazyLoader] ✅ components.js ejecutado correctamente, SitecComponents disponible");
            console.log("[LazyLoader] SitecComponents.createField:", typeof window.SitecComponents.createField);
          }
        } catch (error) {
          console.error("[LazyLoader] ❌ Error cargando components.js:", error);
          console.error("[LazyLoader] Stack:", error.stack);
        }
        
        // Cargar wizard.js después
        console.log("[LazyLoader] 🔄 Cargando wizard.js...");
        try {
          await this.loadModule("/static/frontend/js/wizard.js");
          console.log("[LazyLoader] ✅ wizard.js cargado, verificando ejecución...");
          
          // Verificar inmediatamente si se ejecutó
          await new Promise(resolve => setTimeout(resolve, 100));
          if (!window.__WIZARD_LOADED__) {
            console.error("[LazyLoader] ❌ wizard.js cargado pero __WIZARD_LOADED__ no está definido");
            console.error("[LazyLoader] Verificando si hay errores de sintaxis...");
            
            // Verificar si el script está en el DOM
            const wizardScript = Array.from(document.scripts).find(s => 
              s.src && (s.src.includes('wizard.js') || s.src.endsWith('/wizard.js'))
            );
            
            if (wizardScript) {
              console.error("[LazyLoader] wizard.js está en el DOM pero no se ejecutó");
              console.error("[LazyLoader] URL:", wizardScript.src);
              console.error("[LazyLoader] Verifica la consola para errores de sintaxis");
            } else {
              console.error("[LazyLoader] ❌ wizard.js NO está en el DOM");
            }
          } else {
            console.log("[LazyLoader] ✅ wizard.js ejecutado correctamente");
          }
        } catch (wizardError) {
          console.error("[LazyLoader] ❌ Error cargando wizard.js:", wizardError);
          console.error("[LazyLoader] Stack:", wizardError.stack);
        }
        
        // Cargar el resto en paralelo
        const otherModules = modules.filter((m, i) => i !== componentsIndex && i !== wizardIndex);
        if (otherModules.length > 0) {
          console.log("[LazyLoader] Cargando", otherModules.length, "módulos adicionales...");
          await Promise.all(otherModules.map(path => this.loadModule(path)));
        }
      } else {
        console.warn("[LazyLoader] ⚠️ components.js o wizard.js no están en la lista de módulos");
        if (componentsIndex === -1) {
          console.warn("[LazyLoader] components.js NO está en la lista - verifica getModulesForCurrentPage()");
        }
        if (wizardIndex === -1) {
          console.warn("[LazyLoader] wizard.js NO está en la lista - verifica getModulesForCurrentPage()");
        }
        // Si no hay dependencia crítica, cargar todos en paralelo
        await this.loadModules(modules);
      }
      console.log("[LazyLoader] ✅ Módulos cargados:", modules.length);
    } catch (error) {
      console.error("[LazyLoader] ❌ Error cargando módulos:", error);
      console.error("[LazyLoader] Stack:", error.stack);
    }
  }
}

// Inicializar lazy loader
console.log("%c[LazyLoader] ===== INICIALIZANDO LAZY LOADER =====", "color: purple; font-weight: bold;");
console.log("[LazyLoader] Estado del DOM:", document.readyState);
console.log("[LazyLoader] Ruta actual al inicializar:", window.location.pathname);
console.log("[LazyLoader] URL completa:", window.location.href);

// Función de inicialización
function initLazyLoader() {
  console.log("[LazyLoader] Inicializando LazyLoader...");
  window.lazyLoader = new LazyLoader();
  
  // Verificar qué módulos se van a cargar
  const testLoader = new LazyLoader();
  const testModules = testLoader.getModulesForCurrentPage();
  console.log("[LazyLoader] Módulos que se cargarán:", testModules);
  console.log("[LazyLoader] components.js incluido:", testModules.includes("/static/frontend/js/components.js"));
  
  window.lazyLoader.initialize().catch(error => {
    console.error("[LazyLoader] ❌ Error fatal en initialize():", error);
    console.error("[LazyLoader] Stack:", error.stack);
  });
}

if (document.readyState === "loading") {
  console.log("[LazyLoader] Esperando DOMContentLoaded...");
  document.addEventListener("DOMContentLoaded", () => {
    console.log("[LazyLoader] DOMContentLoaded disparado, inicializando...");
    initLazyLoader();
  });
} else {
  console.log("[LazyLoader] DOM ya está listo, inicializando inmediatamente...");
  initLazyLoader();
}
