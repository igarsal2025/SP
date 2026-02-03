/**
 * sections-projects.js
 * Lista proyectos usando /api/projects/proyectos/
 * Personaliza columnas y acciones según el rol del usuario.
 */

document.addEventListener("DOMContentLoaded", async () => {
  const status = document.getElementById("projectsStatus");
  const table = document.getElementById("projectsListTable");
  const statusFilter = document.getElementById("projectStatusFilter");
  const reloadBtn = document.getElementById("projectsReload");
  const createBtn = document.getElementById("projectsCreateBtn");

  // Obtener contexto del usuario para personalizar columnas
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
    const canEdit = userContext?.permissions?.["projects.edit"] || false;
    const canView = userContext?.permissions?.["projects.view"] || false;

    const baseColumns = [
      { label: "Nombre", value: (r) => r.name || r.code || "--" },
      { label: "Estado", value: (r) => r.status || "--" },
    ];

    // Admin y PM ven más columnas
    if (role === "admin_empresa" || role === "pm") {
      baseColumns.push(
        { label: "Código", value: (r) => r.code || "--" },
        { label: "Progreso", value: (r) => (r.progress_pct ? `${r.progress_pct}%` : "--") },
        { label: "PM", value: (r) => (r.project_manager ? String(r.project_manager).split("@")[0] : "--") },
        { label: "Inicio", value: (r) => r.start_date || "--" },
        { label: "Fin", value: (r) => r.end_date || "--" },
        { label: "Prioridad", value: (r) => r.priority || "--" }
      );
    } else if (role === "supervisor") {
      // Supervisor ve columnas intermedias
      baseColumns.push(
        { label: "Progreso", value: (r) => (r.progress_pct ? `${r.progress_pct}%` : "--") },
        { label: "Inicio", value: (r) => r.start_date || "--" },
        { label: "Fin", value: (r) => r.end_date || "--" }
      );
    } else {
      // Técnico y Cliente ven columnas básicas
      baseColumns.push(
        { label: "Progreso", value: (r) => (r.progress_pct ? `${r.progress_pct}%` : "--") }
      );
    }

    // Agregar columna de acciones si tiene permisos
    if (canEdit || canView) {
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
              window.location.href = `/projects/${r.id}/`;
            };
            container.appendChild(viewBtn);
          }

          if (canEdit) {
            const editBtn = document.createElement("button");
            editBtn.className = "btn btn--ghost";
            editBtn.textContent = "Editar";
            editBtn.onclick = () => {
              window.location.href = `/projects/${r.id}/edit/`;
            };
            container.appendChild(editBtn);
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

      // Usar dataLoader si está disponible para caching
      const url = `/api/projects/proyectos/?${params.toString()}`;
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
      console.error("[Projects] Error:", e);
      
      // Mostrar error con loadingStates si está disponible
      if (window.loadingStates && table) {
        window.loadingStates.showError(
          table,
          "Error al cargar proyectos",
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

  // Botón crear proyecto
  if (createBtn) {
    createBtn.addEventListener("click", () => {
      // Navegar a creación de proyecto
      window.location.href = "/projects/create/";
    });
  }

  load();
});

