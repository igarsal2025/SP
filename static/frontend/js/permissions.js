/**
 * Helper para evaluación de permisos ABAC desde el frontend
 * Integra con el endpoint /api/policies/evaluate/
 */

class PermissionsManager {
    constructor() {
        this.cache = new Map();
        this.cacheTTL = 5 * 60 * 1000; // 5 minutos
    }

    /**
     * Evalúa si una acción está permitida para el usuario actual
     * @param {string} action - Nombre de la acción (ej: "wizard.save", "dashboard.view")
     * @param {boolean} useCache - Si usar caché (default: true)
     * @returns {Promise<{allowed: boolean, policy_id?: string, policy_action?: string}>}
     */
    async evaluate(action, useCache = true) {
        if (!action) {
            return { allowed: false };
        }

        // Verificar caché
        if (useCache) {
            const cached = this.cache.get(action);
            if (cached && Date.now() - cached.timestamp < this.cacheTTL) {
                return cached.decision;
            }
        }

        try {
            const response = await fetch("/api/policies/evaluate/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": this.getCSRFToken(),
                },
                credentials: "include",
                body: JSON.stringify({ action }),
            });

            if (!response.ok) {
                if (response.status === 401 || response.status === 403) {
                    return { allowed: false };
                }
                console.warn(`Error evaluando permiso ${action}:`, response.status);
                return { allowed: false };
            }

            const decision = await response.json();
            
            // Guardar en caché
            if (useCache) {
                this.cache.set(action, {
                    decision,
                    timestamp: Date.now(),
                });
            }

            return decision;
        } catch (error) {
            console.error(`Error evaluando permiso ${action}:`, error);
            // En caso de error, denegar por seguridad
            return { allowed: false };
        }
    }

    /**
     * Evalúa múltiples acciones en paralelo
     * @param {string[]} actions - Array de nombres de acciones
     * @returns {Promise<Map<string, {allowed: boolean}>>}
     */
    async evaluateMultiple(actions) {
        const results = new Map();
        const promises = actions.map(async (action) => {
            const decision = await this.evaluate(action);
            results.set(action, decision);
        });
        await Promise.all(promises);
        return results;
    }

    /**
     * Verifica si una acción está permitida (síncrono desde caché)
     * @param {string} action - Nombre de la acción
     * @returns {boolean|null} - true/false si está en caché, null si no
     */
    isAllowedCached(action) {
        const cached = this.cache.get(action);
        if (cached && Date.now() - cached.timestamp < this.cacheTTL) {
            return cached.decision.allowed;
        }
        return null;
    }

    /**
     * Limpia el caché de permisos
     */
    clearCache() {
        this.cache.clear();
    }

    /**
     * Limpia permisos específicos del caché
     * @param {string|string[]} actions - Acción o array de acciones
     */
    invalidateCache(actions) {
        if (Array.isArray(actions)) {
            actions.forEach((action) => this.cache.delete(action));
        } else {
            this.cache.delete(actions);
        }
    }

    /**
     * Obtiene el token CSRF de las cookies
     * @returns {string}
     */
    getCSRFToken() {
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
}

// Instancia global
const permissionsManager = new PermissionsManager();

/**
 * Helper para usar en componentes
 * @param {string} action - Nombre de la acción
 * @returns {Promise<boolean>}
 */
async function can(action) {
    const decision = await permissionsManager.evaluate(action);
    return decision.allowed;
}

/**
 * Helper para verificar múltiples acciones
 * @param {string[]} actions - Array de acciones
 * @returns {Promise<Map<string, boolean>>}
 */
async function canMultiple(actions) {
    const results = await permissionsManager.evaluateMultiple(actions);
    const allowed = new Map();
    results.forEach((decision, action) => {
        allowed.set(action, decision.allowed);
    });
    return allowed;
}

/**
 * Helper para ocultar/mostrar elementos basado en permisos
 * @param {string} action - Nombre de la acción
 * @param {HTMLElement|string} element - Elemento o selector
 * @param {boolean} showIfAllowed - Si mostrar cuando está permitido (default: true)
 */
async function toggleByPermission(action, element, showIfAllowed = true) {
    const decision = await permissionsManager.evaluate(action);
    const el = typeof element === "string" ? document.querySelector(element) : element;
    if (!el) return;

    const shouldShow = showIfAllowed ? decision.allowed : !decision.allowed;
    if (shouldShow) {
        el.style.display = "";
        el.classList.remove("d-none");
    } else {
        el.style.display = "none";
        el.classList.add("d-none");
    }
}

// Exportar para uso global
window.PermissionsManager = PermissionsManager;
window.permissionsManager = permissionsManager;
window.can = can;
window.canMultiple = canMultiple;
window.toggleByPermission = toggleByPermission;
