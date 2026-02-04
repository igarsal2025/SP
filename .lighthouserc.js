// Configuración de Lighthouse CI para verificación de performance
module.exports = {
  ci: {
    collect: {
      url: ["http://localhost:8000/", "http://localhost:8000/wizard/1/"],
      startServerCommand: "cd backend && python manage.py runserver",
      startServerReadyPattern: "Starting development server",
      startServerReadyTimeout: 30000,
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        // First Contentful Paint (FCP) debe ser < 1s
        "categories:performance": ["error", { minScore: 0.9 }],
        "first-contentful-paint": ["error", { maxNumericValue: 2000 }],
        // Time to Interactive (TTI) debe ser < 2.5s
        "interactive": ["error", { maxNumericValue: 2500 }],
        // Tamaño de JavaScript inicial < 100KB
        "total-byte-weight": ["error", { maxNumericValue: 300000 }],
        // Otras métricas importantes
        "largest-contentful-paint": ["warn", { maxNumericValue: 2500 }],
        "cumulative-layout-shift": ["warn", { maxNumericValue: 0.1 }],
        "speed-index": ["warn", { maxNumericValue: 3000 }],
      },
    },
    upload: {
      target: "temporary-public-storage",
    },
  },
};
