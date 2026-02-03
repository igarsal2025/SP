// Módulo de sincronización con circuit breaker y cifrado
// Circuit Breaker Pattern para manejo de fallos
class CircuitBreaker {
  constructor(options = {}) {
    this.failureThreshold = options.failureThreshold || 5;
    this.resetTimeout = options.resetTimeout || 60000; // 1 minuto
    this.state = "CLOSED"; // CLOSED, OPEN, HALF_OPEN
    this.failureCount = 0;
    this.nextAttempt = Date.now();
  }

  async execute(fn) {
    if (this.state === "OPEN") {
      if (Date.now() < this.nextAttempt) {
        throw new Error("Circuit breaker is OPEN");
      }
      this.state = "HALF_OPEN";
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  onSuccess() {
    this.failureCount = 0;
    this.state = "CLOSED";
  }

  onFailure() {
    this.failureCount++;
    if (this.failureCount >= this.failureThreshold) {
      this.state = "OPEN";
      this.nextAttempt = Date.now() + this.resetTimeout;
    }
  }
}

// Cifrado simple para datos sensibles (AES no disponible en browser, usar btoa/atob como placeholder)
// En producción, usar Web Crypto API o librería como crypto-js
const Encryption = {
  // Placeholder: en producción usar Web Crypto API
  encrypt: (data) => {
    try {
      return btoa(JSON.stringify(data));
    } catch {
      return data;
    }
  },
  decrypt: (encrypted) => {
    try {
      return JSON.parse(atob(encrypted));
    } catch {
      return encrypted;
    }
  },
};

// Sync Manager con reintentos exponenciales
class SyncManager {
  constructor() {
    this.circuitBreaker = new CircuitBreaker({
      failureThreshold: 5,
      resetTimeout: 60000,
    });
    this.maxRetries = 3;
    this.baseDelay = 1000; // 1 segundo
  }

  async syncWithRetry(steps, resolution = null) {
    let attempt = 0;
    let lastError;

    while (attempt < this.maxRetries) {
      try {
        return await this.circuitBreaker.execute(() => this.syncRequest(steps, resolution));
      } catch (error) {
        lastError = error;
        attempt++;
        if (attempt < this.maxRetries) {
          const delay = this.baseDelay * Math.pow(2, attempt - 1); // Backoff exponencial
          await this.sleep(delay);
        }
      }
    }

    throw lastError;
  }

  async syncRequest(steps, resolution) {
    const response = await fetch("/api/wizard/sync/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include", // Incluir cookies de sesión
      body: JSON.stringify({ steps, resolution }),
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Usuario no autenticado, redirigir al login
        window.location.href = "/";
        throw new Error("Sesión expirada");
      } else if (response.status === 403) {
        // Usuario autenticado pero sin permisos - no redirigir
        throw new Error("Sin permisos para sincronizar");
      }
      throw new Error(`Sync failed: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  }

  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// Estado de sincronización por registro
class SyncStatusTracker {
  constructor() {
    this.statuses = new Map(); // step -> { status, timestamp, error }
  }

  setStatus(step, status, error = null) {
    this.statuses.set(step, {
      status, // 'pending', 'syncing', 'synced', 'error'
      timestamp: new Date().toISOString(),
      error,
    });
  }

  getStatus(step) {
    return this.statuses.get(step) || { status: "pending", timestamp: null, error: null };
  }

  getAllStatuses() {
    return Array.from(this.statuses.entries()).map(([step, data]) => ({
      step,
      ...data,
    }));
  }

  clear() {
    this.statuses.clear();
  }
}

// Exportar para uso en wizard.js
window.SyncManager = SyncManager;
window.SyncStatusTracker = SyncStatusTracker;
window.Encryption = Encryption;
