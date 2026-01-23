/**
 * data-loader.js
 * Optimización de carga de datos: debouncing, batching y caching.
 */

class DataLoader {
  constructor() {
    this.cache = new Map();
    this.pendingRequests = new Map();
    this.debounceTimers = new Map();
    this.batchQueue = [];
    this.batchTimer = null;
    this.cacheTTL = 60000; // 1 minuto por defecto
  }

  /**
   * Obtiene datos de una URL con caché y deduplicación de requests.
   * @param {string} url - URL a obtener
   * @param {object} options - Opciones (cache, ttl, etc.)
   * @returns {Promise<any>}
   */
  async fetchWithCache(url, options = {}) {
    const {
      cache = true,
      ttl = this.cacheTTL,
      forceRefresh = false,
    } = options;

    // Verificar caché
    if (cache && !forceRefresh) {
      const cached = this.cache.get(url);
      if (cached && Date.now() - cached.timestamp < ttl) {
        return Promise.resolve(cached.data);
      }
    }

    // Si ya hay un request pendiente para esta URL, reutilizarlo
    if (this.pendingRequests.has(url)) {
      return this.pendingRequests.get(url);
    }

    // Crear nuevo request
    const requestPromise = fetch(url, {
      credentials: "include",
      ...options.fetchOptions,
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
        
        // Guardar en caché
        if (cache) {
          this.cache.set(url, {
            data,
            timestamp: Date.now(),
          });
        }
        
        return data;
      })
      .finally(() => {
        // Limpiar request pendiente
        this.pendingRequests.delete(url);
      });

    this.pendingRequests.set(url, requestPromise);
    return requestPromise;
  }

  /**
   * Debounce: retrasa la ejecución de una función hasta que no haya más llamadas.
   * @param {string} key - Clave única para el debounce
   * @param {Function} fn - Función a ejecutar
   * @param {number} delay - Delay en ms
   */
  debounce(key, fn, delay = 300) {
    if (this.debounceTimers.has(key)) {
      clearTimeout(this.debounceTimers.get(key));
    }

    const timer = setTimeout(() => {
      fn();
      this.debounceTimers.delete(key);
    }, delay);

    this.debounceTimers.set(key, timer);
  }

  /**
   * Batch: agrupa múltiples requests en uno solo.
   * @param {string} url - URL base para el batch
   * @param {object} params - Parámetros a incluir
   * @param {number} delay - Delay antes de ejecutar el batch
   * @returns {Promise<any>}
   */
  async batchRequest(url, params, delay = 100) {
    return new Promise((resolve, reject) => {
      this.batchQueue.push({ url, params, resolve, reject });

      if (this.batchTimer) {
        clearTimeout(this.batchTimer);
      }

      this.batchTimer = setTimeout(async () => {
        const queue = [...this.batchQueue];
        this.batchQueue = [];
        this.batchTimer = null;

        try {
          // Agrupar parámetros
          const allParams = new URLSearchParams();
          queue.forEach((item) => {
            Object.entries(item.params).forEach(([key, value]) => {
              allParams.append(key, value);
            });
          });

          const response = await fetch(`${url}?${allParams.toString()}`, {
            credentials: "include",
          });

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
          }

          const data = await response.json();
          
          // Resolver todas las promesas con el mismo resultado
          queue.forEach((item) => {
            item.resolve(data);
          });
        } catch (error) {
          queue.forEach((item) => {
            item.reject(error);
          });
        }
      }, delay);
    });
  }

  /**
   * Limpia el caché.
   * @param {string} url - URL específica a limpiar, o null para limpiar todo
   */
  clearCache(url = null) {
    if (url) {
      this.cache.delete(url);
    } else {
      this.cache.clear();
    }
  }

  /**
   * Limpia caché expirado.
   */
  clearExpiredCache() {
    const now = Date.now();
    for (const [key, value] of this.cache.entries()) {
      if (now - value.timestamp > this.cacheTTL) {
        this.cache.delete(key);
      }
    }
  }
}

// Inicializar data loader
window.dataLoader = new DataLoader();

// Limpiar caché expirado cada 5 minutos
setInterval(() => {
  window.dataLoader.clearExpiredCache();
}, 5 * 60 * 1000);
