// PWA: Registro de Service Worker y manejo de instalación
(function () {
  if (!("serviceWorker" in navigator)) {
    console.warn("[PWA] Service Workers no soportados");
    return;
  }

  // Registrar Service Worker
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/sw.js", { scope: "/" })
      .then((registration) => {
        console.log("[PWA] Service Worker registrado:", registration.scope);

        // Verificar actualizaciones periódicamente
        setInterval(() => {
          registration.update();
        }, 60000); // Cada minuto

        // Escuchar actualizaciones
        registration.addEventListener("updatefound", () => {
          const newWorker = registration.installing;
          newWorker.addEventListener("statechange", () => {
            if (newWorker.state === "installed" && navigator.serviceWorker.controller) {
              console.log("[PWA] Nueva versión disponible");
              // Opcional: mostrar notificación al usuario
            }
          });
        });
      })
      .catch((error) => {
        console.error("[PWA] Error registrando Service Worker:", error);
      });

    // Escuchar mensajes del Service Worker
    navigator.serviceWorker.addEventListener("message", (event) => {
      console.log("[PWA] Mensaje del SW:", event.data);
    });
  });

  // Manejar instalación de PWA
  let deferredPrompt;
  window.addEventListener("beforeinstallprompt", (e) => {
    e.preventDefault();
    deferredPrompt = e;
    // Opcional: mostrar botón de instalación
    const installBtn = document.getElementById("installPWA");
    if (installBtn) {
      installBtn.style.display = "block";
      installBtn.addEventListener("click", () => {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
          if (choiceResult.outcome === "accepted") {
            console.log("[PWA] Usuario aceptó instalar");
          }
          deferredPrompt = null;
          installBtn.style.display = "none";
        });
      });
    }
  });

  // Detectar si la app está instalada
  window.addEventListener("appinstalled", () => {
    console.log("[PWA] App instalada");
  });
})();
