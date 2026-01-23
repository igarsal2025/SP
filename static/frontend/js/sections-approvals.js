/**
 * sections-approvals.js
 * Vista de aprobaciones: lista reportes "submitted" con acciones de aprobar/rechazar.
 */

document.addEventListener("DOMContentLoaded", async () => {
  const status = document.getElementById("approvalsStatus");
  const table = document.getElementById("approvalsTable");

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
    const canApprove = userContext?.permissions?.["reports.approve"] || false;

    const columns = [
      { label: "Proyecto", value: (r) => r.project_name || r.project || "--" },
      { label: "Semana", value: (r) => r.week_start || "--" },
      { label: "Técnico", value: (r) => r.technician_name || r.technician || "--" },
      { label: "Progreso", value: (r) => (r.progress_pct ? `${r.progress_pct}%` : "--") },
      { label: "Enviado", value: (r) => r.submitted_at || r.created_at || "--" },
    ];

    // Agregar columna de acciones si puede aprobar
    if (canApprove) {
      columns.push({
        label: "Acciones",
        render: (r) => {
          const container = document.createElement("div");
          container.className = "component-inline";
          container.style.gap = "0.5rem";

          const approveBtn = document.createElement("button");
          approveBtn.className = "btn btn--primary";
          approveBtn.textContent = "Aprobar";
          approveBtn.onclick = () => {
            if (confirm("¿Aprobar este reporte?")) {
              fetch(`/api/reports/reportes/${r.id}/approve/`, {
                method: "POST",
                credentials: "include",
              })
                .then((res) => {
                  if (res.ok) {
                    setStatus("Reporte aprobado", "success");
                    load();
                  } else {
                    setStatus("Error al aprobar", "error");
                  }
                })
                .catch((e) => {
                  console.error("Error al aprobar:", e);
                  setStatus("Error al aprobar", "error");
                });
            }
          };
          container.appendChild(approveBtn);

          const rejectBtn = document.createElement("button");
          rejectBtn.className = "btn btn--ghost";
          rejectBtn.textContent = "Rechazar";
          rejectBtn.onclick = () => {
            const reason = prompt("Motivo del rechazo (opcional):");
            if (reason !== null) {
              // Usar endpoint de rechazo
              fetch(`/api/reports/reportes/${r.id}/reject/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ reason: reason || "" }),
              })
                .then((res) => {
                  if (res.ok) {
                    setStatus("Reporte rechazado", "warn");
                    load();
                  } else {
                    res.json().then((error) => {
                      setStatus("Error al rechazar: " + (error.error || error.detail || "Error desconocido"), "error");
                    });
                  }
                })
                .catch((e) => {
                  console.error("Error al rechazar:", e);
                  setStatus("Error al rechazar", "error");
                });
            }
          };
          container.appendChild(rejectBtn);

          const viewBtn = document.createElement("button");
          viewBtn.className = "btn btn--ghost";
          viewBtn.textContent = "Ver";
          viewBtn.onclick = () => {
            window.location.href = `/reports/${r.id}/`;
          };
          container.appendChild(viewBtn);

          return container;
        },
      });
    }

    return columns;
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
      params.set("status", "submitted");
      
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
      console.error("[Approvals] Error:", e);
      
      // Mostrar error con loadingStates si está disponible
      if (window.loadingStates && table) {
        window.loadingStates.showError(
          table,
          "Error al cargar aprobaciones",
          "Por favor, verifica tu conexión e intenta nuevamente."
        );
      } else {
        setStatus("Error al cargar", "error");
        renderTable([]);
      }
    }
  };

  load();
});

