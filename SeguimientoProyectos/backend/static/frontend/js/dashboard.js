document.addEventListener("DOMContentLoaded", () => {
  const status = document.getElementById("dashboardStatus");
  const container = document.getElementById("dashboardKpis");
  const alertsContainer = document.getElementById("dashboardAlerts");
  const comparativesContainer = document.getElementById("dashboardComparatives");
  if (!status || !container) return;

  const setStatus = (text, level = "info") => {
    status.textContent = text;
    status.setAttribute("data-level", level);
  };

  const addCard = (title, value, helper = "") => {
    const card = document.createElement("div");
    card.className = "component-card";
    const h = document.createElement("div");
    h.className = "panel-title";
    h.textContent = title;
    const v = document.createElement("div");
    v.style.fontSize = "1.5rem";
    v.style.fontWeight = "600";
    v.textContent = value;
    card.appendChild(h);
    card.appendChild(v);
    if (helper) {
      const small = document.createElement("div");
      small.className = "helper";
      small.textContent = helper;
      card.appendChild(small);
    }
    container.appendChild(card);
  };

  const addAlert = (alert) => {
    if (!alertsContainer) return;
    const row = document.createElement("div");
    row.className = "status";
    row.dataset.level = alert.level || "info";
    row.textContent = alert.message || "";
    alertsContainer.appendChild(row);
  };

  const addComparativeCard = (title, delta, pct = null) => {
    if (!comparativesContainer) return;
    const card = document.createElement("div");
    card.className = "component-card";
    const h = document.createElement("div");
    h.className = "panel-title";
    h.textContent = title;
    const v = document.createElement("div");
    v.style.fontSize = "1.25rem";
    v.style.fontWeight = "600";
    const sign = delta > 0 ? "+" : "";
    v.textContent = `${sign}${delta}`;
    card.appendChild(h);
    card.appendChild(v);
    if (pct !== null && pct !== undefined) {
      const helper = document.createElement("div");
      helper.className = "helper";
      const pctSign = pct > 0 ? "+" : "";
      helper.textContent = `${pctSign}${pct}% vs periodo anterior`;
      card.appendChild(helper);
    }
    comparativesContainer.appendChild(card);
  };

  const parseResults = (payload) => {
    if (Array.isArray(payload)) return payload;
    if (payload && Array.isArray(payload.results)) return payload.results;
    return [];
  };

  const formatDate = (value) => {
    if (!value) return "--";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return date.toLocaleDateString("es-MX");
  };

  const renderTable = (table, columns, rows) => {
    table.innerHTML = "";
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    columns.forEach((col) => {
      const th = document.createElement("th");
      th.textContent = col.label;
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    if (!rows.length) {
      const emptyRow = document.createElement("tr");
      const emptyCell = document.createElement("td");
      emptyCell.colSpan = columns.length;
      emptyCell.textContent = "Sin datos disponibles";
      emptyRow.appendChild(emptyCell);
      tbody.appendChild(emptyRow);
    } else {
      rows.forEach((row) => {
        const tr = document.createElement("tr");
        columns.forEach((col) => {
          const td = document.createElement("td");
          if (typeof col.render === "function") {
            const node = col.render(row);
            if (node) {
              td.appendChild(node);
            } else {
              td.textContent = "--";
            }
          } else {
            const value = typeof col.value === "function" ? col.value(row) : row[col.value];
            td.textContent = value ?? "--";
          }
          tr.appendChild(td);
        });
        tbody.appendChild(tr);
      });
    }
    table.appendChild(tbody);
  };

  const state = {
    projectsPage: 1,
    reportsPage: 1,
    pageSize: 10,
    historyPeriod: 30,
    roiPeriod: 30,
  };

  const updatePager = (type, payload) => {
    const count = payload?.count ?? 0;
    const pageInfo = document.getElementById(`${type}PageInfo`);
    const prevBtn = document.getElementById(`${type}Prev`);
    const nextBtn = document.getElementById(`${type}Next`);
    const currentPage = type === "projects" ? state.projectsPage : state.reportsPage;
    const totalPages = Math.max(1, Math.ceil(count / state.pageSize));
    if (pageInfo) {
      pageInfo.textContent = `Página ${currentPage} de ${totalPages}`;
    }
    if (prevBtn) prevBtn.disabled = currentPage <= 1;
    if (nextBtn) nextBtn.disabled = currentPage >= totalPages;
  };

  const loadDashboard = async () => {
    setStatus("Cargando...", "info");
    container.innerHTML = "";
    if (alertsContainer) alertsContainer.innerHTML = "";
    if (comparativesContainer) comparativesContainer.innerHTML = "";
    try {
      const projectStatus = document.getElementById("projectStatusFilter")?.value || "";
      const reportStatus = document.getElementById("reportStatusFilter")?.value || "";
      const projectParams = new URLSearchParams();
      const reportParams = new URLSearchParams();
      if (projectStatus) projectParams.set("status", projectStatus);
      if (reportStatus) reportParams.set("status", reportStatus);
      projectParams.set("page", String(state.projectsPage));
      projectParams.set("page_size", String(state.pageSize));
      reportParams.set("page", String(state.reportsPage));
      reportParams.set("page_size", String(state.pageSize));

      const [kpiResponse, projectsResponse, reportsResponse] = await Promise.all([
        fetch("/api/dashboard/"),
        fetch(`/api/projects/proyectos/?${projectParams.toString()}`),
        fetch(`/api/reports/reportes/?${reportParams.toString()}`),
      ]);

      if (!kpiResponse.ok) {
        setStatus("Error al cargar", "error");
        return;
      }
      const data = await kpiResponse.json();
      addCard("Proyectos totales", data.projects_total ?? 0);
      addCard("En progreso", data.projects_in_progress ?? 0);
      addCard("Retrasados", data.projects_overdue ?? 0);
      addCard("Reportes 7 dias", data.reports_last_7d ?? 0);
      addCard("Reportes enviados 7 dias", data.reports_submitted_last_7d ?? 0);
      addCard("Riesgos altos", data.risks_high ?? 0);

      if (alertsContainer) {
        const alerts = data.alerts || [];
        if (!alerts.length) {
          addAlert({ level: "success", message: "Sin alertas relevantes." });
        } else {
          alerts.forEach(addAlert);
        }
      }
      if (comparativesContainer) {
        const comps = data.comparatives || {};
        const periodDays = data.period_days ?? 7;
        if (periodDays !== 7 && comps.reports_last_period_delta !== undefined) {
          addComparativeCard(
            `Reportes ${periodDays} dias (delta)`,
            comps.reports_last_period_delta ?? 0,
            comps.reports_last_period_pct ?? null
          );
          addComparativeCard(
            `Reportes enviados ${periodDays} dias (delta)`,
            comps.reports_submitted_last_period_delta ?? 0,
            comps.reports_submitted_last_period_pct ?? null
          );
          if (comps.projects_created_last_period_delta !== undefined) {
            addComparativeCard(
              `Proyectos creados ${periodDays} dias (delta)`,
              comps.projects_created_last_period_delta ?? 0,
              comps.projects_created_last_period_pct ?? null
            );
          }
          if (comps.risks_high_last_period_delta !== undefined) {
            addComparativeCard(
              `Riesgos altos ${periodDays} dias (delta)`,
              comps.risks_high_last_period_delta ?? 0,
              comps.risks_high_last_period_pct ?? null
            );
          }
        }
        addComparativeCard(
          "Reportes 7 dias (delta)",
          comps.reports_last_7d_delta ?? 0,
          comps.reports_last_7d_pct ?? null
        );
        addComparativeCard(
          "Reportes enviados 7 dias (delta)",
          comps.reports_submitted_last_7d_delta ?? 0,
          comps.reports_submitted_last_7d_pct ?? null
        );
        addComparativeCard(
          "Reportes 30 dias (delta)",
          comps.reports_last_30d_delta ?? 0,
          comps.reports_last_30d_pct ?? null
        );
      }

      const projectsTable = document.getElementById("projectsTable");
      if (projectsTable && projectsResponse.ok) {
        const projectPayload = await projectsResponse.json();
        const projects = parseResults(projectPayload);
        renderTable(
          projectsTable,
          [
            {
              label: "Codigo",
              render: (row) => {
                const link = document.createElement("a");
                link.href = `/wizard/1/?project=${row.id}`;
                link.textContent = row.code || "--";
                return link;
              },
            },
            { label: "Nombre", value: "name" },
            { label: "Estado", value: "status" },
            { label: "% Avance", value: "progress_pct" },
            { label: "Inicio", value: (row) => formatDate(row.start_date) },
            { label: "Fin", value: (row) => formatDate(row.end_date) },
          ],
          projects
        );
        updatePager("projects", projectPayload);
      }

      const reportsTable = document.getElementById("reportsTable");
      if (reportsTable && reportsResponse.ok) {
        const reportPayload = await reportsResponse.json();
        const reports = parseResults(reportPayload);
        renderTable(
          reportsTable,
          [
            {
              label: "Proyecto",
              render: (row) => {
                const link = document.createElement("a");
                link.href = `/wizard/1/?report=${row.id}`;
                link.textContent = row.project_name || "--";
                return link;
              },
            },
            { label: "Semana", value: (row) => formatDate(row.week_start) },
            { label: "% Avance", value: "progress_pct" },
            { label: "Estado", value: "status" },
            { label: "Tecnico", value: "technician" },
            { label: "Creado", value: (row) => formatDate(row.created_at) },
          ],
          reports
        );
        updatePager("reports", reportPayload);
      }

      setStatus("Actualizado", "success");
    } catch {
      setStatus("Sin conexion", "warning");
    }
  };

  const loadHistory = async () => {
    const table = document.getElementById("historyTable");
    if (!table) return;
    try {
      const params = new URLSearchParams();
      params.set("period_days", String(state.historyPeriod));
      params.set("limit", "12");
      const response = await fetch(`/api/dashboard/history/?${params.toString()}`);
      if (!response.ok) return;
      const rows = await response.json();
      renderTable(
        table,
        [
          { label: "Fecha corte", value: (row) => formatDate(row.computed_at) },
          { label: "Reportes (periodo)", value: (row) => row.payload?.reports_last_period ?? "--" },
          {
            label: "Reportes enviados",
            value: (row) => row.payload?.reports_submitted_last_period ?? "--",
          },
          { label: "Proyectos retrasados", value: (row) => row.payload?.projects_overdue ?? "--" },
        ],
        rows || []
      );
    } catch {
      // ignore
    }
  };

  const loadAggregates = async () => {
    const table = document.getElementById("aggregateTable");
    if (!table) return;
    try {
      const params = new URLSearchParams();
      params.set("limit", "12");
      const response = await fetch(`/api/dashboard/aggregates/?${params.toString()}`);
      if (!response.ok) return;
      const rows = await response.json();
      renderTable(
        table,
        [
          { label: "Periodo", value: (row) => `${formatDate(row.period_start)} - ${formatDate(row.period_end)}` },
          { label: "Reportes (periodo)", value: (row) => row.payload?.reports_last_period ?? "--" },
          {
            label: "Reportes enviados",
            value: (row) => row.payload?.reports_submitted_last_period ?? "--",
          },
          { label: "Proyectos retrasados", value: (row) => row.payload?.projects_overdue ?? "--" },
        ],
        rows || []
      );
    } catch {
      // ignore
    }
  };

  const loadRoi = async () => {
    const table = document.getElementById("roiTable");
    const kpiContainer = document.getElementById("roiKpis");
    if (!table || !kpiContainer) return;
    kpiContainer.innerHTML = "";
    try {
      const params = new URLSearchParams();
      params.set("period_days", String(state.roiPeriod));
      const response = await fetch(`/api/roi/?${params.toString()}`);
      if (!response.ok) return;
      const data = await response.json();
      const addRoiCard = (title, value) => {
        const card = document.createElement("div");
        card.className = "component-card";
        const h = document.createElement("div");
        h.className = "panel-title";
        h.textContent = title;
        const v = document.createElement("div");
        v.style.fontSize = "1.25rem";
        v.style.fontWeight = "600";
        v.textContent = value ?? "--";
        card.appendChild(h);
        card.appendChild(v);
        kpiContainer.appendChild(card);
      };
      addRoiCard("ROI promedio (%)", data.avg_roi_pct ?? "--");
      addRoiCard("Presupuesto estimado", data.total_estimated ?? 0);
      addRoiCard("Presupuesto actual", data.total_actual ?? 0);
      addRoiCard("Proyectos con sobrecosto", data.overruns ?? 0);

      renderTable(
        table,
        [
          { label: "Codigo", value: "code" },
          { label: "Proyecto", value: "name" },
          { label: "Estimado", value: "estimated" },
          { label: "Actual", value: "actual" },
          { label: "ROI %", value: "roi_pct" },
          { label: "% Avance", value: "progress_pct" },
        ],
        data.projects || []
      );
    } catch {
      // ignore
    }
  };

  const exportRoi = () => {
    const link = document.createElement("a");
    link.href = `/api/roi/export/?period_days=${state.roiPeriod}&limit=50`;
    link.click();
  };

  loadDashboard();
  loadHistory();
  loadAggregates();
  loadRoi();

  document.getElementById("projectStatusFilter")?.addEventListener("change", () => {
    state.projectsPage = 1;
    loadDashboard();
  });
  document.getElementById("reportStatusFilter")?.addEventListener("change", () => {
    state.reportsPage = 1;
    loadDashboard();
  });
  document.getElementById("projectsPrev")?.addEventListener("click", () => {
    state.projectsPage = Math.max(1, state.projectsPage - 1);
    loadDashboard();
  });
  document.getElementById("projectsNext")?.addEventListener("click", () => {
    state.projectsPage += 1;
    loadDashboard();
  });
  document.getElementById("reportsPrev")?.addEventListener("click", () => {
    state.reportsPage = Math.max(1, state.reportsPage - 1);
    loadDashboard();
  });
  document.getElementById("reportsNext")?.addEventListener("click", () => {
    state.reportsPage += 1;
    loadDashboard();
  });
  document.getElementById("historyPeriodSelect")?.addEventListener("change", (event) => {
    state.historyPeriod = parseInt(event.target.value || "30", 10);
    loadHistory();
  });
  document.getElementById("roiPeriodSelect")?.addEventListener("change", (event) => {
    state.roiPeriod = parseInt(event.target.value || "30", 10);
    loadRoi();
  });
  document.getElementById("roiExportBtn")?.addEventListener("click", () => {
    exportRoi();
  });
});
