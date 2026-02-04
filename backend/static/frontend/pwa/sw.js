// Service Worker para SITEC Web PWA
// Versión: 1.0.0
const CACHE_NAME = "sitec-web-v1";
const RUNTIME_CACHE = "sitec-runtime-v1";
const OFFLINE_PAGE = "/offline.html";

// Recursos críticos para cache inicial
const CRITICAL_ASSETS = [
  "/",
  "/static/frontend/css/tokens.css",
  "/static/frontend/css/wizard.css",
  "/static/frontend/js/wizard.js",
  "/static/frontend/pwa/manifest.json",
];

// Estrategia: Cache First para assets estáticos, Network First para API
const CACHE_FIRST_PATTERNS = [
  /\/static\//,
  /\.(?:png|jpg|jpeg|svg|gif|webp|woff|woff2|ttf|eot)$/,
];

const NETWORK_FIRST_PATTERNS = [
  /\/api\//,
  /\/wizard\//,
];

// Instalación: cache de recursos críticos
self.addEventListener("install", (event) => {
  console.log("[SW] Instalando Service Worker");
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("[SW] Cacheando recursos críticos");
      return cache.addAll(CRITICAL_ASSETS).catch((err) => {
        console.warn("[SW] Error cacheando algunos recursos:", err);
      });
    })
  );
  self.skipWaiting();
});

// Activación: limpiar caches antiguos
self.addEventListener("activate", (event) => {
  console.log("[SW] Activando Service Worker");
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME && name !== RUNTIME_CACHE)
          .map((name) => {
            console.log("[SW] Eliminando cache antiguo:", name);
            return caches.delete(name);
          })
      );
    })
  );
  return self.clients.claim();
});

// Fetch: estrategias de cache
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Ignorar requests no-GET y cross-origin
  if (request.method !== "GET" || url.origin !== self.location.origin) {
    return;
  }

  // API endpoints: Network First con fallback a cache
  if (NETWORK_FIRST_PATTERNS.some((pattern) => pattern.test(url.pathname))) {
    event.respondWith(networkFirstStrategy(request));
    return;
  }

  // Assets estáticos: Cache First
  if (CACHE_FIRST_PATTERNS.some((pattern) => pattern.test(url.pathname))) {
    event.respondWith(cacheFirstStrategy(request));
    return;
  }

  // Por defecto: Network First
  event.respondWith(networkFirstStrategy(request));
});

// Estrategia: Network First (para API y páginas dinámicas)
async function networkFirstStrategy(request) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log("[SW] Network falló, usando cache:", request.url);
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    // Si es una página HTML y no hay cache, mostrar offline
    if (request.headers.get("accept")?.includes("text/html")) {
      const offlinePage = await caches.match(OFFLINE_PAGE);
      if (offlinePage) return offlinePage;
    }
    throw error;
  }
}

// Estrategia: Cache First (para assets estáticos)
async function cacheFirstStrategy(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.error("[SW] Error fetch:", request.url, error);
    throw error;
  }
}

// Mensajes desde el cliente (para actualizar cache, etc.)
self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
  if (event.data && event.data.type === "CLEAR_CACHE") {
    caches.delete(CACHE_NAME);
    caches.delete(RUNTIME_CACHE);
  }
});
