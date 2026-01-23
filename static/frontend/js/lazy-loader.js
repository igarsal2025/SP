/**
 * lazy-loader.js
 * Sistema de carga diferida (lazy loading) para componentes JavaScript.
 * Carga solo los scripts necesarios según la página actual.
 */

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
    // Verificar si ya existe un script con esta src
    const existingScripts = document.querySelectorAll(`script[src="${modulePath}"]`);
    if (existingScripts.length > 0) {
      return true;
    }
    
    // Verificar si está en la lista de módulos cargados
    return this.loadedModules.has(modulePath);
  }

  /**
   * Carga un módulo JavaScript de forma asíncrona.
   * @param {string} modulePath - Ruta del módulo a cargar
   * @returns {Promise<void>}
   */
  async loadModule(modulePath) {
    // Si ya está cargado en el DOM, retornar inmediatamente
    if (this.isScriptAlreadyLoaded(modulePath)) {
      this.loadedModules.add(modulePath);
      return Promise.resolve();
    }

    // Si ya está en proceso de carga, retornar la promesa existente
    if (this.loadingPromises.has(modulePath)) {
      return this.loadingPromises.get(modulePath);
    }

    // Crear nueva promesa de carga
    const loadPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = modulePath;
      script.async = true;
      script.defer = true;
      
      script.onload = () => {
        this.loadedModules.add(modulePath);
        this.loadingPromises.delete(modulePath);
        resolve();
      };
      
      script.onerror = () => {
        this.loadingPromises.delete(modulePath);
        reject(new Error(`Failed to load module: ${modulePath}`));
      };
      
      document.head.appendChild(script);
    });

    this.loadingPromises.set(modulePath, loadPromise);
    return loadPromise;
  }

  /**
   * Carga múltiples módulos en paralelo.
   * @param {string[]} modulePaths - Array de rutas de módulos
   * @returns {Promise<void[]>}
   */
  async loadModules(modulePaths) {
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

    // Módulos base siempre necesarios (si no están ya cargados)
    const baseModules = [
      "/static/frontend/js/performance.js",
      "/static/frontend/js/data-loader.js",
      "/static/frontend/js/loading-states.js",
      "/static/frontend/js/role-based-ui.js",
    ];

    baseModules.forEach(module => {
      if (!this.isScriptAlreadyLoaded(module)) {
        modules.push(module);
      }
    });

    // Módulos según ruta (solo si no están ya en el template)
    if (path.startsWith("/dashboard")) {
      if (!this.isScriptAlreadyLoaded("/static/frontend/js/navigation.js")) {
        modules.push("/static/frontend/js/navigation.js");
      }
      // dashboard.js y dashboard-lite.js se cargan en los templates específicos
    } else if (path.startsWith("/wizard")) {
      const wizardModules = [
        "/static/frontend/js/pwa.js",
        "/static/frontend/js/sync.js",
        "/static/frontend/js/analytics.js",
        "/static/frontend/js/permissions.js",
        "/static/frontend/js/components.js",
        "/static/frontend/js/wizard.js",
      ];
      wizardModules.forEach(module => {
        if (!this.isScriptAlreadyLoaded(module)) {
          modules.push(module);
        }
      });
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

    return modules;
  }

  /**
   * Inicializa la carga diferida según la página actual.
   */
  async initialize() {
    const modules = this.getModulesForCurrentPage();
    try {
      await this.loadModules(modules);
      console.log("[LazyLoader] Módulos cargados:", modules.length);
    } catch (error) {
      console.error("[LazyLoader] Error cargando módulos:", error);
    }
  }
}

// Inicializar lazy loader
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    window.lazyLoader = new LazyLoader();
    window.lazyLoader.initialize();
  });
} else {
  window.lazyLoader = new LazyLoader();
  window.lazyLoader.initialize();
}
