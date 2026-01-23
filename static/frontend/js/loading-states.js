/**
 * loading-states.js
 * Mejora el feedback visual con estados de carga, skeleton screens y mensajes de error claros.
 */

class LoadingStates {
  constructor() {
    this.loadingElements = new Map();
  }

  /**
   * Muestra un estado de carga en un elemento.
   * @param {HTMLElement|string} element - Elemento o selector
   * @param {string} message - Mensaje opcional
   */
  showLoading(element, message = "Cargando...") {
    const el = typeof element === "string" ? document.querySelector(element) : element;
    if (!el) return;

    // Guardar contenido original
    if (!this.loadingElements.has(el)) {
      this.loadingElements.set(el, {
        originalContent: el.innerHTML,
        originalDisplay: el.style.display,
      });
    }

    // Mostrar spinner y mensaje
    el.innerHTML = `
      <div class="loading-state" style="display: flex; align-items: center; gap: var(--space-2); padding: var(--space-4); justify-content: center;">
        <div class="loading-spinner"></div>
        <span>${message}</span>
      </div>
    `;
    el.style.display = el.style.display || "block";
  }

  /**
   * Muestra un skeleton screen en lugar de contenido.
   * @param {HTMLElement|string} element - Elemento o selector
   * @param {number} lines - Número de líneas skeleton
   */
  showSkeleton(element, lines = 3) {
    const el = typeof element === "string" ? document.querySelector(element) : element;
    if (!el) return;

    if (!this.loadingElements.has(el)) {
      this.loadingElements.set(el, {
        originalContent: el.innerHTML,
        originalDisplay: el.style.display,
      });
    }

    const skeletonHTML = Array.from({ length: lines }, (_, i) => {
      const width = i === lines - 1 ? "60%" : "100%";
      return `<div class="skeleton" style="height: 20px; width: ${width}; margin-bottom: var(--space-2);"></div>`;
    }).join("");

    el.innerHTML = `<div class="skeleton-container">${skeletonHTML}</div>`;
    el.style.display = el.style.display || "block";
  }

  /**
   * Restaura el contenido original del elemento.
   * @param {HTMLElement|string} element - Elemento o selector
   */
  hideLoading(element) {
    const el = typeof element === "string" ? document.querySelector(element) : element;
    if (!el || !this.loadingElements.has(el)) return;

    const saved = this.loadingElements.get(el);
    el.innerHTML = saved.originalContent;
    el.style.display = saved.originalDisplay;
    this.loadingElements.delete(el);
  }

  /**
   * Muestra un mensaje de error claro.
   * @param {HTMLElement|string} element - Elemento o selector
   * @param {string} message - Mensaje de error
   * @param {string} details - Detalles opcionales
   */
  showError(element, message, details = null) {
    const el = typeof element === "string" ? document.querySelector(element) : element;
    if (!el) return;

    const errorHTML = `
      <div class="error-state" style="padding: var(--space-4); text-align: center;">
        <div style="color: var(--color-error); font-size: 2rem; margin-bottom: var(--space-2);">⚠️</div>
        <div style="font-weight: 600; color: var(--color-error); margin-bottom: var(--space-2);">${message}</div>
        ${details ? `<div style="font-size: var(--font-size-sm); color: var(--color-muted);">${details}</div>` : ""}
        <button class="btn btn--ghost" onclick="location.reload()" style="margin-top: var(--space-3);">Reintentar</button>
      </div>
    `;

    el.innerHTML = errorHTML;
  }

  /**
   * Muestra un mensaje de éxito.
   * @param {HTMLElement|string} element - Elemento o selector
   * @param {string} message - Mensaje de éxito
   */
  showSuccess(element, message) {
    const el = typeof element === "string" ? document.querySelector(element) : element;
    if (!el) return;

    const successHTML = `
      <div class="success-state" style="padding: var(--space-4); text-align: center;">
        <div style="color: var(--color-success); font-size: 2rem; margin-bottom: var(--space-2);">✓</div>
        <div style="font-weight: 600; color: var(--color-success);">${message}</div>
      </div>
    `;

    el.innerHTML = successHTML;

    // Auto-ocultar después de 3 segundos
    setTimeout(() => {
      if (this.loadingElements.has(el)) {
        this.hideLoading(el);
      }
    }, 3000);
  }

  /**
   * Agrega estado de carga a un botón.
   * @param {HTMLElement|string} button - Botón o selector
   */
  setButtonLoading(button, loading = true) {
    const btn = typeof button === "string" ? document.querySelector(button) : button;
    if (!btn) return;

    if (loading) {
      btn.classList.add("btn--loading");
      btn.disabled = true;
      if (!btn.dataset.originalText) {
        btn.dataset.originalText = btn.textContent;
      }
      btn.textContent = "Cargando...";
    } else {
      btn.classList.remove("btn--loading");
      btn.disabled = false;
      if (btn.dataset.originalText) {
        btn.textContent = btn.dataset.originalText;
        delete btn.dataset.originalText;
      }
    }
  }
}

// Inicializar loading states
window.loadingStates = new LoadingStates();
