/**
 * role-based-ui.js
 * 
 * Maneja la lógica de visibilidad de elementos según el rol del usuario.
 * Proporciona funciones para mostrar/ocultar elementos y inicializar la UI
 * basada en el contexto del usuario obtenido del servidor.
 */

(function() {
    'use strict';

    // Cache del contexto del usuario
    let userContext = null;
    let contextLoaded = false;

    /**
     * Obtiene el contexto del usuario desde el servidor.
     * @returns {Promise<Object>} Contexto del usuario con permisos y UI config
     */
    async function getUserContext() {
        if (contextLoaded && userContext) {
            return Promise.resolve(userContext);
        }

        try {
            const response = await fetch('/api/user/context/', {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Accept': 'application/json',
                }
            });

            if (!response.ok) {
                if (response.status === 401) {
                    // Usuario no autenticado
                    return null;
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            userContext = data;
            contextLoaded = true;
            return userContext;
        } catch (error) {
            console.error('[RoleBasedUI] Error obteniendo contexto de usuario:', error);
            return null;
        }
    }

    /**
     * Muestra u oculta un elemento según el rol del usuario.
     * @param {HTMLElement|string} element - Elemento o selector CSS
     * @param {string|string[]} allowedRoles - Rol(es) permitido(s)
     * @param {Object} context - Contexto del usuario (opcional, se obtiene si no se proporciona)
     */
    async function showForRole(element, allowedRoles, context = null) {
        const el = typeof element === 'string' ? document.querySelector(element) : element;
        if (!el) {
            console.warn('[RoleBasedUI] Elemento no encontrado:', element);
            return;
        }

        // Obtener contexto si no se proporciona
        if (!context) {
            context = await getUserContext();
        }

        if (!context) {
            // Sin contexto = ocultar
            el.style.display = 'none';
            return;
        }

        const userRole = context.profile?.role;
        if (!userRole) {
            el.style.display = 'none';
            return;
        }

        // Convertir allowedRoles a array si es string
        const roles = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];

        // Mostrar si el rol está en la lista permitida
        if (roles.includes(userRole)) {
            el.style.display = '';
        } else {
            el.style.display = 'none';
        }
    }

    /**
     * Verifica si el usuario tiene un permiso específico.
     * @param {string} permissionName - Nombre del permiso
     * @param {Object} context - Contexto del usuario (opcional)
     * @returns {Promise<boolean>} True si tiene el permiso
     */
    async function hasPermission(permissionName, context = null) {
        if (!context) {
            context = await getUserContext();
        }

        if (!context) {
            return false;
        }

        return context.permissions?.[permissionName] === true;
    }

    /**
     * Verifica si una sección del dashboard está visible para el usuario.
     * @param {string} sectionName - Nombre de la sección
     * @param {Object} context - Contexto del usuario (opcional)
     * @returns {Promise<boolean>} True si la sección está visible
     */
    async function isDashboardSectionVisible(sectionName, context = null) {
        if (!context) {
            context = await getUserContext();
        }

        if (!context) {
            return false;
        }

        const sections = context.ui_config?.dashboard_sections || [];
        return sections.includes(sectionName);
    }

    /**
     * Verifica si un elemento de navegación está disponible para el usuario.
     * @param {string} navItem - Nombre del elemento de navegación
     * @param {Object} context - Contexto del usuario (opcional)
     * @returns {Promise<boolean>} True si el elemento está disponible
     */
    async function canAccessNavigation(navItem, context = null) {
        if (!context) {
            context = await getUserContext();
        }

        if (!context) {
            return false;
        }

        const navigation = context.ui_config?.navigation || [];
        return navigation.includes(navItem);
    }

    /**
     * Obtiene el modo del wizard para el usuario actual.
     * @param {Object} context - Contexto del usuario (opcional)
     * @returns {Promise<string>} 'full' o 'readonly'
     */
    async function getWizardMode(context = null) {
        if (!context) {
            context = await getUserContext();
        }

        if (!context) {
            return 'readonly';
        }

        return context.ui_config?.wizard_mode || 'readonly';
    }

    /**
     * Inicializa la UI basada en el rol del usuario.
     * Oculta elementos que no son accesibles según los permisos.
     */
    async function initializeRoleBasedUI() {
        const context = await getUserContext();
        
        if (!context) {
            console.warn('[RoleBasedUI] No se pudo obtener contexto de usuario');
            return;
        }

        const userRole = context.profile?.role;
        console.log('[RoleBasedUI] Inicializando UI para rol:', userRole);

        // Ocultar elementos según permisos
        // Ejemplo: ocultar botones de crear si no tiene permiso
        const createButtons = document.querySelectorAll('[data-requires-permission="projects.create"]');
        const canCreate = await hasPermission('projects.create', context);
        createButtons.forEach(btn => {
            btn.style.display = canCreate ? '' : 'none';
        });

        // Ocultar secciones del dashboard no permitidas
        const dashboardSections = document.querySelectorAll('[data-dashboard-section]');
        for (const section of dashboardSections) {
            const sectionName = section.getAttribute('data-dashboard-section');
            const isVisible = await isDashboardSectionVisible(sectionName, context);
            section.style.display = isVisible ? '' : 'none';
        }

        // Ocultar elementos de navegación no permitidos
        const navItems = document.querySelectorAll('[data-nav-item]');
        for (const navItem of navItems) {
            const itemName = navItem.getAttribute('data-nav-item');
            const canAccess = await canAccessNavigation(itemName, context);
            navItem.style.display = canAccess ? '' : 'none';
        }

        // Configurar modo del wizard
        const wizardMode = await getWizardMode(context);
        if (wizardMode === 'readonly') {
            const wizardEditElements = document.querySelectorAll('[data-wizard-edit]');
            wizardEditElements.forEach(el => {
                el.style.display = 'none';
            });
        }

        // Disparar evento personalizado cuando la UI está inicializada
        document.dispatchEvent(new CustomEvent('roleBasedUIInitialized', {
            detail: { context, role: userRole }
        }));
    }

    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeRoleBasedUI);
    } else {
        initializeRoleBasedUI();
    }

    // Exportar funciones para uso global
    window.RoleBasedUI = {
        getUserContext,
        showForRole,
        hasPermission,
        isDashboardSectionVisible,
        canAccessNavigation,
        getWizardMode,
        initializeRoleBasedUI,
    };

})();
