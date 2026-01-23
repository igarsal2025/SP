// Analytics de pasos completados y tiempo por paso
class WizardAnalytics {
  constructor() {
    this.stepTimes = new Map(); // step -> { startTime, endTime, duration }
    this.stepStartTimes = new Map();
    this.completedSteps = new Set();
    this.events = [];
    this.maxEvents = 25;
    this.flushInterval = 30000;
    this.lastFlush = Date.now();
    this.sessionId = this.getSessionId();
  }

  startStep(step) {
    this.stepStartTimes.set(step, Date.now());
  }

  endStep(step) {
    const startTime = this.stepStartTimes.get(step);
    if (!startTime) return;

    const endTime = Date.now();
    const duration = endTime - startTime;

    this.stepTimes.set(step, {
      startTime,
      endTime,
      duration,
    });
    this.completedSteps.add(step);
    this.stepStartTimes.delete(step);

    // Guardar en IndexedDB
    this.saveToIndexedDB(step, duration);
  }

  getAverageTimeForStep(step) {
    // Obtener tiempos históricos de IndexedDB
    return this.loadFromIndexedDB(step).then((times) => {
      if (!times || times.length === 0) return null;
      const sum = times.reduce((acc, t) => acc + t, 0);
      return Math.round(sum / times.length / 1000); // en segundos
    });
  }

  getTotalTime() {
    let total = 0;
    this.stepTimes.forEach((data) => {
      total += data.duration;
    });
    return total;
  }

  getSessionId() {
    const key = "sitec_wizard_session_id";
    const stored = localStorage.getItem(key);
    if (stored) return stored;
    const id = `${Date.now()}_${Math.random().toString(16).slice(2, 10)}`;
    localStorage.setItem(key, id);
    return id;
  }

  trackEvent(name, metadata = {}) {
    this.events.push({
      name,
      timestamp: Date.now(),
      metadata,
    });
    if (
      this.events.length >= this.maxEvents ||
      Date.now() - this.lastFlush >= this.flushInterval
    ) {
      this.sendToServer(true);
    }
  }

  async saveToIndexedDB(step, duration) {
    const db = await this.openAnalyticsDB();
    return new Promise((resolve) => {
      const tx = db.transaction("step_times", "readwrite");
      const store = tx.objectStore("step_times");
      const record = {
        step,
        duration,
        timestamp: Date.now(),
      };
      store.add(record);
      tx.oncomplete = () => resolve();
    });
  }

  async loadFromIndexedDB(step) {
    const db = await this.openAnalyticsDB();
    return new Promise((resolve) => {
      const tx = db.transaction("step_times", "readonly");
      const store = tx.objectStore("step_times");
      const index = store.index("step");
      const req = index.getAll(step);
      req.onsuccess = () => {
        const times = req.result.map((r) => r.duration);
        resolve(times);
      };
      req.onerror = () => resolve([]);
    });
  }

  openAnalyticsDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open("sitec_analytics_db", 1);
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains("step_times")) {
          const store = db.createObjectStore("step_times", { keyPath: "id", autoIncrement: true });
          store.createIndex("step", "step", { unique: false });
        }
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async sendToServer(silent = false) {
    const data = {
      step_times: Array.from(this.stepTimes.entries()).map(([step, data]) => ({
        step,
        ...data,
      })),
      completed_steps: Array.from(this.completedSteps),
      total_time: this.getTotalTime(),
      events: this.events,
      session_id: this.sessionId,
      path: window.location.pathname,
    };

    try {
      if (!data.step_times.length && !data.events.length) return;
      const payload = JSON.stringify(data);
      if (navigator.sendBeacon) {
        const blob = new Blob([payload], { type: "application/json" });
        navigator.sendBeacon("/api/wizard/analytics/", blob);
      } else {
        const response = await fetch("/api/wizard/analytics/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: payload,
          keepalive: true,
        });
        // Si el usuario no está autenticado, no hacer nada (evitar redirección en analytics)
        if (response.status === 403 || response.status === 401) {
          return;
        }
      }
      this.events = [];
      this.lastFlush = Date.now();
    } catch (error) {
      if (!silent) {
        console.warn("[Analytics] Error enviando datos:", error);
      }
    }
  }
}

window.WizardAnalytics = WizardAnalytics;
