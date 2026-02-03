/**
 * dashboard-lite.js
 *
 * Dashboard ligero (sin APIs /api/dashboard/*), pensado para roles que no tienen
 * permisos gerenciales. Muestra listas de proyectos y reportes usando sus APIs.
 */

document.addEventListener("DOMContentLoaded", () => {
  const status = document.getElementById("dashboardStatus");
  const projectsTable = document.getElementById("projectsTable");
  const reportsTable = document.getElementById("reportsTable");

  const setStatus = (text, level = "info") => {
    if (!status) return;
    status.textContent = text;
    status.setAttribute("data-level", level);
  };

  const renderSimpleTable = (table, columns, rows) => {
    if (!table) return;
    table.innerHTML = "";
    const thead = document.createElement("thead");
    const trh = document.createElement("tr");
    columns.forEach((c) => {
      const th = document.createElement("th");
      th.textContent = c.label;
      trh.appendChild(th);
    });
    thead.appendChild(trh);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    if (!rows || !rows.length) {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = columns.length;
      td.textContent = "Sin datos disponibles";
      tr.appendChild(td);
      tbody.appendChild(tr);
    } else {
      rows.forEach((row) => {
        const tr = document.createElement("tr");
        columns.forEach((c) => {
          const td = document.createElement("td");
          const value = typeof c.value === "function" ? c.value(row) : row[c.value];
          td.textContent = value ?? "--";
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
    }
    table.appendChild(tbody);
  };

  const parseResults = (payload) => {
    if (Array.isArray(payload)) return payload;
    if (payload && Array.isArray(payload.results)) return payload.results;
    return [];
  };

  const loadLite = async () => {
    setStatus("Cargando...", "info");
    
    // Mostrar skeleton mientras carga
    if (window.loadingStates) {
      if (projectsTable) window.loadingStates.showSkeleton(projectsTable, 3);
      if (reportsTable) window.loadingStates.showSkeleton(reportsTable, 3);
    }

    try {
      // Usar dataLoader si está disponible para cargar en paralelo con caché
      const projectsUrl = "/api/projects/proyectos/?page_size=10";
      const reportsUrl = "/api/reports/reportes/?page_size=10";

      let projectsData = null;
      let reportsData = null;

      if (window.dataLoader) {
        // Cargar en paralelo con caché
        [projectsData, reportsData] = await Promise.all([
          window.dataLoader.fetchWithCache(projectsUrl, { cache: true, ttl: 30000 }).catch(() => null),
          window.dataLoader.fetchWithCache(reportsUrl, { cache: true, ttl: 30000 }).catch(() => null),
        ]);
      } else {
        // Fallback a fetch normal
        const [projectsRes, reportsRes] = await Promise.all([
          fetch(projectsUrl, { credentials: "include" }),
          fetch(reportsUrl, { credentials: "include" }),
        ]);

        if (!projectsRes.ok && !reportsRes.ok) {
          setStatus("Sin acceso o sin datos", "warn");
          if (window.loadingStates) {
            if (projectsTable) window.loadingStates.hideLoading(projectsTable);
            if (reportsTable) window.loadingStates.hideLoading(reportsTable);
          }
          return;
        }

        projectsData = projectsRes.ok ? await projectsRes.json() : null;
        reportsData = reportsRes.ok ? await reportsRes.json() : null;
      }

      // Ocultar skeleton
      if (window.loadingStates) {
        if (projectsTable) window.loadingStates.hideLoading(projectsTable);
        if (reportsTable) window.loadingStates.hideLoading(reportsTable);
      }

      renderSimpleTable(
        projectsTable,
        [
          { label: "Proyecto", value: (r) => r.name || r.code || "--" },
          { label: "Estado", value: (r) => r.status || "--" },
        ],
        parseResults(projectsData)
      );

      renderSimpleTable(
        reportsTable,
        [
          { label: "Proyecto", value: (r) => r.project_name || r.project || "--" },
          { label: "Semana", value: (r) => r.week_start || "--" },
          { label: "Estado", value: (r) => r.status || "--" },
        ],
        parseResults(reportsData)
      );

      setStatus("Listo", "success");
    } catch (e) {
      console.error("[Dashboard Lite] Error:", e);
      
      // Mostrar error con loadingStates si está disponible
      if (window.loadingStates) {
        if (projectsTable) {
          window.loadingStates.showError(
            projectsTable,
            "Error al cargar proyectos",
            "Por favor, verifica tu conexión e intenta nuevamente."
          );
        }
        if (reportsTable) {
          window.loadingStates.showError(
            reportsTable,
            "Error al cargar reportes",
            "Por favor, verifica tu conexión e intenta nuevamente."
          );
        }
      } else {
        setStatus("Error al cargar", "error");
      }
    }
  };

  loadLite();
});

