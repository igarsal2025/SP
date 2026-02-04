/**
 * sections-reports.js
 * Lista reportes usando /api/reports/reportes/
 * Personaliza columnas y acciones según el rol del usuario.
 */

document.addEventListener("DOMContentLoaded", async () => {
  const status = document.getElementById("reportsStatus");
  const table = document.getElementById("reportsListTable");
  const statusFilter = document.getElementById("reportStatusFilter");
  const reloadBtn = document.getElementById("reportsReload");
  const createBtn = document.getElementById("reportsCreateBtn");

  // Obtener contexto del usuario
  let userContext = null;
  if (window.RoleBasedUI) {
    userContext = await window.RoleBasedUI.getUserContext();
  }

  const setStatus = (text, level = "info") => {
    if (!status) return;
    status.textContent = text;
    status.setAttribute("data-level", level);
  };

  // Determinar columnas según rol
  const getColumns = () => {
    const role = userContext?.profile?.role;
    const canApprove = userContext?.permissions?.["reports.approve"] || false;
    const canSubmit = userContext?.permissions?.["wizard.submit"] || false;
    const canView = userContext?.permissions?.["reports.view"] || false;

    const baseColumns = [
      { label: "Proyecto", value: (r) => r.project_name || r.project || "--" },
      { label: "Semana", value: (r) => r.week_start || "--" },
      { label: "Estado", value: (r) => r.status || "--" },
    ];

    // Admin, PM y Supervisor ven más columnas
    if (role === "admin_empresa" || role === "pm" || role === "supervisor") {
      baseColumns.push(
        { label: "Técnico", value: (r) => r.technician_name || r.technician || "--" },
        { label: "Progreso", value: (r) => (r.progress_pct ? `${r.progress_pct}%` : "--") },
        { label: "Creado", value: (r) => r.created_at || "--" }
      );
    } else if (role === "tecnico") {
      // Técnico ve columnas básicas
      baseColumns.push(
        { label: "Progreso", value: (r) => (r.progress_pct ? `${r.progress_pct}%` : "--") }
      );
    }
    // Cliente solo ve las columnas base (sin progreso ni técnico)

    // Agregar columna de acciones
    if (canView || canApprove || canSubmit) {
      baseColumns.push({
        label: "Acciones",
        render: (r) => {
          const container = document.createElement("div");
          container.className = "component-inline";
          container.style.gap = "0.5rem";

          if (canView) {
            const viewBtn = document.createElement("button");
            viewBtn.className = "btn btn--ghost";
            viewBtn.textContent = "Ver";
            viewBtn.onclick = () => {
              window.location.href = `/reports/${r.id}/`;
            };
            container.appendChild(viewBtn);
          }

          // Solo técnico puede enviar reportes propios
          if (canSubmit && role === "tecnico" && r.status === "draft") {
            const submitBtn = document.createElement("button");
            submitBtn.className = "btn btn--secondary";
            submitBtn.textContent = "Enviar";
            submitBtn.onclick = () => {
              if (confirm("¿Enviar este reporte para aprobación?")) {
                fetch(`/api/reports/reportes/${r.id}/submit/`, {
                  method: "POST",
                  credentials: "include",
                })
                  .then((res) => res.json())
                  .then(() => {
                    load();
                  })
                  .catch((e) => console.error("Error al enviar:", e));
              }
            };
            container.appendChild(submitBtn);
          }

          // Solo supervisor/PM/admin pueden aprobar
          if (canApprove && r.status === "submitted") {
            const approveBtn = document.createElement("button");
            approveBtn.className = "btn btn--primary";
            approveBtn.textContent = "Aprobar";
            approveBtn.onclick = () => {
              if (confirm("¿Aprobar este reporte?")) {
                fetch(`/api/reports/reportes/${r.id}/approve/`, {
                  method: "POST",
                  credentials: "include",
                })
                  .then((res) => res.json())
                  .then(() => {
                    load();
                  })
                  .catch((e) => console.error("Error al aprobar:", e));
              }
            };
            container.appendChild(approveBtn);
          }

          return container;
        },
      });
    }

    return baseColumns;
  };

  const renderTable = (rows) => {
    if (!table) return;
    table.innerHTML = "";

    const columns = getColumns();

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
    if (!rows.length) {
      const tr = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = columns.length;
      td.textContent = "Sin datos disponibles";
      tr.appendChild(td);
      tbody.appendChild(tr);
    } else {
      rows.forEach((r) => {
        const tr = document.createElement("tr");
        columns.forEach((c) => {
          const td = document.createElement("td");
          if (typeof c.render === "function") {
            const node = c.render(r);
            if (node) {
              td.appendChild(node);
            } else {
              td.textContent = "--";
            }
          } else if (typeof c.value === "function") {
            td.textContent = c.value(r) ?? "--";
          } else {
            td.textContent = r[c.value] ?? "--";
          }
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

  const load = async () => {
    setStatus("Cargando...", "info");
    
    // Mostrar skeleton mientras carga
    if (window.loadingStates && table) {
      window.loadingStates.showSkeleton(table, 5);
    }

    try {
      const params = new URLSearchParams();
      params.set("page_size", "50");
      const value = statusFilter?.value || "";
      if (value) params.set("status", value);

      // Usar dataLoader si está disponible
      const url = `/api/reports/reportes/?${params.toString()}`;
      let data;
      
      if (window.dataLoader) {
        data = await window.dataLoader.fetchWithCache(url, { cache: true, ttl: 30000 });
      } else {
        const res = await fetch(url, { credentials: "include" });
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        data = await res.json();
      }

      // Ocultar skeleton
      if (window.loadingStates && table) {
        window.loadingStates.hideLoading(table);
      }

      renderTable(parseResults(data));
      setStatus("Listo", "success");
    } catch (e) {
      console.error("[Reports] Error:", e);
      
      // Mostrar error con loadingStates si está disponible
      if (window.loadingStates && table) {
        window.loadingStates.showError(
          table,
          "Error al cargar reportes",
          "Por favor, verifica tu conexión e intenta nuevamente."
        );
      } else {
        setStatus("Error al cargar", "error");
        renderTable([]);
      }
    }
  };

  reloadBtn?.addEventListener("click", load);
  statusFilter?.addEventListener("change", load);

  // Botón crear reporte
  if (createBtn) {
    createBtn.addEventListener("click", () => {
      // Navegar al wizard para crear nuevo reporte
      window.location.href = "/wizard/";
    });
  }

  load();
});

