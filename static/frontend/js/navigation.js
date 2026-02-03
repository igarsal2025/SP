/**
 * navigation.js
 * 
 * Sistema de navegación principal para SITEC.
 * Gestiona la navegación entre secciones según el rol del usuario.
 */

(function() {
    'use strict';

    /**
     * NavigationManager - Gestiona la navegación principal
     */
    class NavigationManager {
        constructor() {
            this.currentSection = null;
            this.userContext = null;
            this.navigationItems = new Map();
        }

        /**
         * Inicializa el gestor de navegación.
         * @param {Object} userContext - Contexto del usuario
         */
        async initialize(userContext = null) {
            // Obtener contexto si no se proporciona
            if (!userContext && window.RoleBasedUI) {
                userContext = await window.RoleBasedUI.getUserContext();
            }

            this.userContext = userContext;

            if (!userContext) {
                console.warn('[Navigation] No se pudo obtener contexto de usuario');
                return;
            }

            // Configurar navegación según el rol
            this.setupNavigation();
            
            // Detectar sección actual
            this.detectCurrentSection();
            
            // Configurar event listeners
            this.setupEventListeners();

            console.log('[Navigation] Navegación inicializada para rol:', userContext.profile?.role);
        }

        /**
         * Configura los elementos de navegación según el rol.
         */
        setupNavigation() {
            if (!this.userContext) {
                return;
            }

            const allowedNavigation = this.userContext.ui_config?.navigation || [];
            const navContainer = document.querySelector('[data-navigation]');

            if (!navContainer) {
                // Si no hay contenedor de navegación, crear uno básico
                this.createNavigationContainer();
                return;
            }

            // Ocultar elementos de navegación no permitidos
            const navItems = navContainer.querySelectorAll('[data-nav-item]');
            navItems.forEach(item => {
                const itemName = item.getAttribute('data-nav-item');
                if (allowedNavigation.includes(itemName)) {
                    item.style.display = '';
                    this.navigationItems.set(itemName, item);
                } else {
                    item.style.display = 'none';
                }
            });
        }

        /**
         * Crea un contenedor de navegación básico si no existe.
         */
        createNavigationContainer() {
            // Buscar el header o crear uno
            let header = document.querySelector('header.topbar');
            if (!header) {
                header = document.querySelector('header');
            }

            if (!header) {
                console.warn('[Navigation] No se encontró header para agregar navegación');
                return;
            }

            // Crear contenedor de navegación
            const navContainer = document.createElement('nav');
            navContainer.setAttribute('data-navigation', '');
            navContainer.className = 'main-navigation';

            const allowedNavigation = this.userContext.ui_config?.navigation || [];
            
            // Mapeo de nombres de navegación a etiquetas y URLs
            const navMap = {
                'dashboard': { label: 'Dashboard', url: '/dashboard/' },
                'wizard': { label: 'Wizard', url: '/wizard/' },
                'projects': { label: 'Proyectos', url: '/projects/' },
                'reports': { label: 'Reportes', url: '/reports/' },
                'documents': { label: 'Documentos', url: '/documents/' },
                'approvals': { label: 'Aprobaciones', url: '/reports/approvals/' },
                'configuration': { label: 'Configuración', url: '/configuration/' },
                'users': { label: 'Usuarios', url: '/users/' },
            };

            allowedNavigation.forEach(navItem => {
                const config = navMap[navItem];
                if (config) {
                    const link = document.createElement('a');
                    link.href = config.url;
                    link.textContent = config.label;
                    link.setAttribute('data-nav-item', navItem);
                    link.className = 'nav-link';
                    navContainer.appendChild(link);
                    this.navigationItems.set(navItem, link);
                }
            });

            // Insertar después del header
            header.insertAdjacentElement('afterend', navContainer);
        }

        /**
         * Detecta la sección actual basándose en la URL.
         */
        detectCurrentSection() {
            const path = window.location.pathname;
            
            if (path.includes('/dashboard')) {
                this.currentSection = 'dashboard';
            } else if (path.includes('/wizard')) {
                this.currentSection = 'wizard';
            } else if (path.includes('/projects')) {
                this.currentSection = 'projects';
            } else if (path.includes('/reports')) {
                this.currentSection = 'reports';
            } else if (path.includes('/documents')) {
                this.currentSection = 'documents';
            } else if (path.includes('/configuration')) {
                this.currentSection = 'configuration';
            } else if (path.includes('/users')) {
                this.currentSection = 'users';
            }

            // Marcar elemento activo
            this.setActiveSection(this.currentSection);
        }

        /**
         * Establece la sección activa en la navegación.
         * @param {string} sectionName - Nombre de la sección
         */
        setActiveSection(sectionName) {
            // Remover clase activa de todos los elementos
            this.navigationItems.forEach(item => {
                item.classList.remove('active');
            });

            // Agregar clase activa al elemento correspondiente
            const activeItem = this.navigationItems.get(sectionName);
            if (activeItem) {
                activeItem.classList.add('active');
            }
        }

        /**
         * Navega a una sección específica.
         * @param {string} sectionName - Nombre de la sección
         */
        navigateToSection(sectionName) {
            // Verificar si la sección está permitida
            if (!this.canAccessSection(sectionName)) {
                console.warn(`[Navigation] Sección no permitida: ${sectionName}`);
                return;
            }

            const navMap = {
                'dashboard': '/dashboard/',
                'wizard': '/wizard/',
                'projects': '/projects/',
                'reports': '/reports/',
                'documents': '/documents/',
                'approvals': '/reports/approvals/',
                'configuration': '/configuration/',
                'users': '/users/',
            };

            const url = navMap[sectionName];
            if (url) {
                window.location.href = url;
            }
        }

        /**
         * Verifica si el usuario puede acceder a una sección.
         * @param {string} sectionName - Nombre de la sección
         * @returns {boolean} True si puede acceder
         */
        canAccessSection(sectionName) {
            if (!this.userContext) {
                return false;
            }

            const allowedNavigation = this.userContext.ui_config?.navigation || [];
            return allowedNavigation.includes(sectionName);
        }

        /**
         * Configura los event listeners para la navegación.
         */
        setupEventListeners() {
            // Interceptar clics en enlaces de navegación
            this.navigationItems.forEach((item, sectionName) => {
                item.addEventListener('click', (e) => {
                    e.preventDefault();
                    this.navigateToSection(sectionName);
                });
            });

            // Escuchar cambios de sección desde otros componentes
            document.addEventListener('navigationChange', (e) => {
                const sectionName = e.detail?.section;
                if (sectionName) {
                    this.navigateToSection(sectionName);
                }
            });
        }

        /**
         * Muestra solo la navegación permitida para un rol específico.
         * @param {string} role - Rol del usuario
         */
        showNavigationForRole(role) {
            // Esta función puede ser llamada para actualizar la navegación
            // después de un cambio de rol (si se implementa)
            console.log('[Navigation] Actualizando navegación para rol:', role);
            // La lógica real se maneja en setupNavigation()
        }
    }

    // Crear instancia global
    const navigationManager = new NavigationManager();

    // Inicializar cuando el DOM esté listo y el contexto esté disponible
    function initializeNavigation() {
        if (window.RoleBasedUI) {
            window.RoleBasedUI.getUserContext().then(context => {
                navigationManager.initialize(context);
            });
        } else {
            // Esperar a que RoleBasedUI esté disponible
            document.addEventListener('roleBasedUIInitialized', (e) => {
                navigationManager.initialize(e.detail.context);
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeNavigation);
    } else {
        initializeNavigation();
    }

    // Exportar para uso global
    window.NavigationManager = NavigationManager;
    window.navigationManager = navigationManager;

})();
