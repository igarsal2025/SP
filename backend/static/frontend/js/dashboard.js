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

  const addComparativeCard = (title, delta, pct = null, currentValue = null) => {
    if (!comparativesContainer) return;
    const card = document.createElement("div");
    card.className = "component-card";
    const h = document.createElement("div");
    h.className = "panel-title";
    h.textContent = title;
    
    // Mostrar valor actual si está disponible
    if (currentValue !== null && currentValue !== undefined) {
      const current = document.createElement("div");
      current.style.fontSize = "1.5rem";
      current.style.fontWeight = "600";
      current.textContent = currentValue;
      card.appendChild(h);
      card.appendChild(current);
    }
    
    const v = document.createElement("div");
    v.style.fontSize = "1.25rem";
    v.style.fontWeight = "600";
    v.style.marginTop = currentValue !== null ? "0.5rem" : "0";
    const sign = delta > 0 ? "+" : "";
    v.textContent = `Delta: ${sign}${delta}`;
    if (currentValue === null) {
      card.appendChild(h);
    }
    card.appendChild(v);
    
    if (pct !== null && pct !== undefined) {
      const helper = document.createElement("div");
      helper.className = "helper";
      helper.style.marginTop = "0.25rem";
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

  // Cargar lista de proyectos para el filtro
  const loadProjectsForFilter = async () => {
    const projectFilter = document.getElementById("dashboardProjectFilter");
    if (!projectFilter) return;
    
    try {
      const response = await fetch("/api/projects/proyectos/?page_size=100");
      if (!response.ok) return;
      const data = await response.json();
      const projects = Array.isArray(data) ? data : (data.results || []);
      
      // Limpiar opciones existentes (excepto "Todos")
      projectFilter.innerHTML = '<option value="">Todos los proyectos</option>';
      
      projects.forEach(project => {
        const option = document.createElement("option");
        option.value = project.id;
        option.textContent = project.name || project.code || `Proyecto ${project.id}`;
        projectFilter.appendChild(option);
      });
    } catch (error) {
      console.error("Error loading projects for filter:", error);
    }
  };

  const loadDashboard = async (filters = {}) => {
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

      // Construir URL de KPIs con filtros
      const kpiParams = new URLSearchParams();
      if (filters.project_id) kpiParams.set("project_id", filters.project_id);
      if (filters.start_date) kpiParams.set("start_date", filters.start_date);
      if (filters.end_date) kpiParams.set("end_date", filters.end_date);
      if (filters.period_days) kpiParams.set("period_days", String(filters.period_days));
      
      const kpiUrl = `/api/dashboard/${kpiParams.toString() ? '?' + kpiParams.toString() : ''}`;

      const [kpiResponse, projectsResponse, reportsResponse] = await Promise.all([
        fetch(kpiUrl),
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
        
        // Comparativos período anterior (7 días o personalizado)
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
        
        // Comparativos 7 días
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
        
        // Comparativos mes anterior
        if (comps.reports_month_delta !== undefined) {
          addComparativeCard(
            "Reportes mes actual (vs mes anterior)",
            comps.reports_month_delta ?? 0,
            comps.reports_month_pct ?? null,
            comps.reports_month ?? 0
          );
          addComparativeCard(
            "Reportes enviados mes actual (vs mes anterior)",
            comps.reports_submitted_month_delta ?? 0,
            comps.reports_submitted_month_pct ?? null,
            comps.reports_submitted_month ?? 0
          );
          if (comps.projects_created_month_delta !== undefined) {
            addComparativeCard(
              "Proyectos creados mes actual (vs mes anterior)",
              comps.projects_created_month_delta ?? 0,
              comps.projects_created_month_pct ?? null,
              comps.projects_created_month ?? 0
            );
          }
        }
        
        // Comparativos año anterior
        if (comps.reports_year_delta !== undefined) {
          addComparativeCard(
            "Reportes año actual (vs año anterior)",
            comps.reports_year_delta ?? 0,
            comps.reports_year_pct ?? null,
            comps.reports_year ?? 0
          );
          addComparativeCard(
            "Reportes enviados año actual (vs año anterior)",
            comps.reports_submitted_year_delta ?? 0,
            comps.reports_submitted_year_pct ?? null,
            comps.reports_submitted_year ?? 0
          );
          if (comps.projects_created_year_delta !== undefined) {
            addComparativeCard(
              "Proyectos creados año actual (vs año anterior)",
              comps.projects_created_year_delta ?? 0,
              comps.projects_created_year_pct ?? null,
              comps.projects_created_year ?? 0
            );
          }
        }
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
      addRoiCard("ROI promedio (%)", data.avg_roi_pct !== null && data.avg_roi_pct !== undefined ? `${data.avg_roi_pct}%` : "--");
      addRoiCard("Presupuesto estimado", data.total_estimated ? `$${data.total_estimated.toLocaleString()}` : "$0");
      addRoiCard("Presupuesto actual", data.total_actual ? `$${data.total_actual.toLocaleString()}` : "$0");
      addRoiCard("Proyectos con sobrecosto", data.overruns ?? 0);
      
      // Mostrar comparativos si están disponibles
      if (data.comparatives) {
        const comp = data.comparatives;
        if (comp.avg_roi_delta !== null && comp.avg_roi_delta !== undefined) {
          const compCard = document.createElement("div");
          compCard.className = "component-card";
          const h = document.createElement("div");
          h.className = "panel-title";
          h.textContent = "Cambio ROI vs período anterior";
          const v = document.createElement("div");
          v.style.fontSize = "1.25rem";
          v.style.fontWeight = "600";
          const delta = comp.avg_roi_delta;
          v.textContent = `${delta >= 0 ? "+" : ""}${delta}%`;
          v.style.color = delta >= 0 ? "#28a745" : "#dc3545";
          compCard.appendChild(h);
          compCard.appendChild(v);
          kpiContainer.appendChild(compCard);
        }
      }

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

  // Cargar tendencias históricas
  const loadTrends = async () => {
    const container = document.getElementById("trendsContainer");
    if (!container) return;

    const periodType = document.getElementById("trendsPeriodType")?.value || "month";
    const periods = parseInt(document.getElementById("trendsPeriods")?.value || "12", 10);

    container.innerHTML = '<div class="helper">Cargando tendencias...</div>';

    try {
      const response = await fetch(`/api/dashboard/trends/?type=${periodType}&periods=${periods}`);
      if (!response.ok) {
        container.innerHTML = '<div class="status" data-level="error">Error al cargar tendencias</div>';
        return;
      }

      const data = await response.json();
      const trends = data.trends || [];

      if (!trends.length) {
        container.innerHTML = '<div class="helper">No hay datos de tendencias disponibles</div>';
        return;
      }

      // Renderizar gráficos de tendencias
      renderTrendsCharts(container, trends, periodType);
    } catch (error) {
      container.innerHTML = '<div class="status" data-level="error">Error de conexión</div>';
    }
  };

  const renderTrendsCharts = (container, trends, periodType) => {
    container.innerHTML = "";

    // Extraer datos para cada métrica
    const reportsData = trends.map(t => ({
      period: periodType === "month" 
        ? new Date(t.period_start).toLocaleDateString("es-MX", { month: "short", year: "numeric" })
        : new Date(t.computed_at).toLocaleDateString("es-MX", { month: "short", day: "numeric" }),
      value: t.reports || 0,
      delta: t.delta_pct || null
    }));

    const reportsSubmittedData = trends.map(t => ({
      period: periodType === "month"
        ? new Date(t.period_start).toLocaleDateString("es-MX", { month: "short", year: "numeric" })
        : new Date(t.computed_at).toLocaleDateString("es-MX", { month: "short", day: "numeric" }),
      value: t.reports_submitted || 0
    }));

    const projectsData = trends.map(t => ({
      period: periodType === "month"
        ? new Date(t.period_start).toLocaleDateString("es-MX", { month: "short", year: "numeric" })
        : new Date(t.computed_at).toLocaleDateString("es-MX", { month: "short", day: "numeric" }),
      value: t.projects_created || 0
    }));

    const risksData = trends.map(t => ({
      period: periodType === "month"
        ? new Date(t.period_start).toLocaleDateString("es-MX", { month: "short", year: "numeric" })
        : new Date(t.computed_at).toLocaleDateString("es-MX", { month: "short", day: "numeric" }),
      value: t.risks_high || 0
    }));

    // Crear gráficos
    const chartsGrid = document.createElement("div");
    chartsGrid.className = "grid grid-2";
    chartsGrid.style.marginTop = "1rem";

    chartsGrid.appendChild(createTrendChart("Reportes", reportsData));
    chartsGrid.appendChild(createTrendChart("Reportes Enviados", reportsSubmittedData));
    chartsGrid.appendChild(createTrendChart("Proyectos Creados", projectsData));
    chartsGrid.appendChild(createTrendChart("Riesgos Altos", risksData));

    container.appendChild(chartsGrid);
  };

  const createTrendChart = (title, data) => {
    const card = document.createElement("div");
    card.className = "component-card";
    
    // Header con título y botón de exportación
    const header = document.createElement("div");
    header.style.display = "flex";
    header.style.justifyContent = "space-between";
    header.style.alignItems = "center";
    header.style.marginBottom = "0.5rem";
    
    const titleEl = document.createElement("div");
    titleEl.className = "panel-title";
    titleEl.textContent = title;
    header.appendChild(titleEl);
    
    // Botón de exportación
    const exportBtn = document.createElement("button");
    exportBtn.className = "btn btn--ghost";
    exportBtn.style.fontSize = "0.875rem";
    exportBtn.style.padding = "0.25rem 0.5rem";
    exportBtn.textContent = "Exportar";
    exportBtn.title = "Exportar gráfico como PNG o SVG";
    header.appendChild(exportBtn);
    
    card.appendChild(header);

    if (!data.length) {
      const empty = document.createElement("div");
      empty.className = "helper";
      empty.textContent = "Sin datos";
      card.appendChild(empty);
      return card;
    }

    // Calcular valores para el gráfico
    const values = data.map(d => d.value);
    const maxValue = Math.max(...values, 1);
    const minValue = Math.min(...values, 0);
    const range = maxValue - minValue || 1;
    
    // Detectar tendencia significativa
    const firstValue = values[0];
    const lastValue = values[values.length - 1];
    const changePct = firstValue > 0 ? ((lastValue - firstValue) / firstValue) * 100 : 0;
    const isSignificantChange = Math.abs(changePct) > 10; // Cambio > 10%
    const isPositiveTrend = changePct > 0;

    // Crear SVG para el gráfico
    const svgContainer = document.createElement("div");
    svgContainer.style.position = "relative";
    
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", "200");
    svg.setAttribute("viewBox", "0 0 400 200");
    svg.style.display = "block";
    svg.style.marginTop = "0.5rem";
    svg.setAttribute("data-chart-title", title);
    
    // Tooltip
    const tooltip = document.createElement("div");
    tooltip.id = `tooltip-${title.replace(/\s+/g, "-").toLowerCase()}`;
    tooltip.style.position = "absolute";
    tooltip.style.background = "rgba(0, 0, 0, 0.85)";
    tooltip.style.color = "#fff";
    tooltip.style.padding = "0.5rem";
    tooltip.style.borderRadius = "4px";
    tooltip.style.fontSize = "0.875rem";
    tooltip.style.pointerEvents = "none";
    tooltip.style.display = "none";
    tooltip.style.zIndex = "1000";
    tooltip.style.boxShadow = "0 2px 8px rgba(0,0,0,0.2)";
    svgContainer.appendChild(tooltip);

    const width = 400;
    const height = 200;
    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;

    // Eje Y (valores)
    const yAxis = document.createElementNS("http://www.w3.org/2000/svg", "line");
    yAxis.setAttribute("x1", padding);
    yAxis.setAttribute("y1", padding);
    yAxis.setAttribute("x2", padding);
    yAxis.setAttribute("y2", height - padding);
    yAxis.setAttribute("stroke", "#ccc");
    yAxis.setAttribute("stroke-width", "1");
    svg.appendChild(yAxis);

    // Eje X (períodos)
    const xAxis = document.createElementNS("http://www.w3.org/2000/svg", "line");
    xAxis.setAttribute("x1", padding);
    xAxis.setAttribute("y1", height - padding);
    xAxis.setAttribute("x2", width - padding);
    xAxis.setAttribute("y2", height - padding);
    xAxis.setAttribute("stroke", "#ccc");
    xAxis.setAttribute("stroke-width", "1");
    svg.appendChild(xAxis);

    // Línea de tendencia
    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    const points = data.map((d, i) => {
      const x = padding + (i / (data.length - 1 || 1)) * chartWidth;
      const y = height - padding - ((d.value - minValue) / range) * chartHeight;
      return `${i === 0 ? "M" : "L"} ${x} ${y}`;
    }).join(" ");
    path.setAttribute("d", points);
    path.setAttribute("fill", "none");
    path.setAttribute("stroke", "#007bff");
    path.setAttribute("stroke-width", "2");
    svg.appendChild(path);

    // Puntos de datos con tooltips
    data.forEach((d, i) => {
      const x = padding + (i / (data.length - 1 || 1)) * chartWidth;
      const y = height - padding - ((d.value - minValue) / range) * chartHeight;
      
      // Área invisible más grande para facilitar hover
      const hoverArea = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      hoverArea.setAttribute("cx", x);
      hoverArea.setAttribute("cy", y);
      hoverArea.setAttribute("r", "12");
      hoverArea.setAttribute("fill", "transparent");
      hoverArea.style.cursor = "pointer";
      hoverArea.dataset.index = i;
      hoverArea.dataset.value = d.value;
      hoverArea.dataset.period = d.period;
      hoverArea.dataset.delta = d.delta || "";
      
      // Event listeners para tooltip
      hoverArea.addEventListener("mouseenter", (e) => {
        const rect = svg.getBoundingClientRect();
        const svgRect = svgContainer.getBoundingClientRect();
        tooltip.style.display = "block";
        tooltip.style.left = `${rect.left + x - svgRect.left}px`;
        tooltip.style.top = `${rect.top + y - svgRect.top - 40}px`;
        tooltip.innerHTML = `
          <div><strong>${d.period}</strong></div>
          <div>Valor: ${d.value}</div>
          ${d.delta !== null && d.delta !== undefined ? `<div>Delta: ${d.delta >= 0 ? "+" : ""}${d.delta}%</div>` : ""}
        `;
      });
      
      hoverArea.addEventListener("mouseleave", () => {
        tooltip.style.display = "none";
      });
      
      hoverArea.addEventListener("mousemove", (e) => {
        const rect = svg.getBoundingClientRect();
        const svgRect = svgContainer.getBoundingClientRect();
        tooltip.style.left = `${rect.left + x - svgRect.left}px`;
        tooltip.style.top = `${rect.top + y - svgRect.top - 40}px`;
      });
      
      svg.appendChild(hoverArea);
      
      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("cx", x);
      circle.setAttribute("cy", y);
      circle.setAttribute("r", "4");
      circle.setAttribute("fill", "#007bff");
      circle.style.cursor = "pointer";
      circle.style.transition = "r 0.2s";
      svg.appendChild(circle);
      
      // Efecto hover en círculo
      hoverArea.addEventListener("mouseenter", () => {
        circle.setAttribute("r", "6");
        circle.setAttribute("fill", "#0056b3");
      });
      hoverArea.addEventListener("mouseleave", () => {
        circle.setAttribute("r", "4");
        circle.setAttribute("fill", "#007bff");
      });

      // Etiqueta del período (solo algunos para no saturar)
      if (i % Math.ceil(data.length / 6) === 0 || i === data.length - 1) {
        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", x);
        text.setAttribute("y", height - padding + 15);
        text.setAttribute("text-anchor", "middle");
        text.setAttribute("font-size", "10");
        text.setAttribute("fill", "#666");
        text.textContent = d.period;
        svg.appendChild(text);
      }
    });

    // Valor máximo y mínimo
    const maxLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
    maxLabel.setAttribute("x", padding - 5);
    maxLabel.setAttribute("y", padding + 5);
    maxLabel.setAttribute("text-anchor", "end");
    maxLabel.setAttribute("font-size", "10");
    maxLabel.setAttribute("fill", "#666");
    maxLabel.textContent = Math.round(maxValue);
    svg.appendChild(maxLabel);

    const minLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
    minLabel.setAttribute("x", padding - 5);
    minLabel.setAttribute("y", height - padding + 5);
    minLabel.setAttribute("text-anchor", "end");
    minLabel.setAttribute("font-size", "10");
    minLabel.setAttribute("fill", "#666");
    minLabel.textContent = Math.round(minValue);
    svg.appendChild(minLabel);

    svgContainer.appendChild(svg);
    card.appendChild(svgContainer);

    // Estadísticas con alerta visual si hay cambio significativo
    const stats = document.createElement("div");
    stats.className = "helper";
    stats.style.marginTop = "0.5rem";
    const avg = Math.round(values.reduce((a, b) => a + b, 0) / values.length);
    const last = values[values.length - 1];
    const first = values[0];
    const change = first > 0 ? Math.round(((last - first) / first) * 100) : 0;
    
    const changeText = document.createElement("span");
    changeText.textContent = `Cambio: ${change >= 0 ? "+" : ""}${change}%`;
    if (isSignificantChange) {
      changeText.style.color = isPositiveTrend ? "#28a745" : "#dc3545";
      changeText.style.fontWeight = "600";
      changeText.title = isPositiveTrend ? "Tendencia positiva significativa" : "Tendencia negativa significativa";
    }
    
    stats.innerHTML = `Promedio: ${avg} | Último: ${last} | `;
    stats.appendChild(changeText);
    card.appendChild(stats);
    
    // Alerta visual si hay cambio significativo
    if (isSignificantChange) {
      const alert = document.createElement("div");
      alert.className = "status";
      alert.dataset.level = isPositiveTrend ? "success" : "warning";
      alert.style.marginTop = "0.5rem";
      alert.style.fontSize = "0.875rem";
      alert.textContent = isPositiveTrend 
        ? `⚠️ Tendencia positiva: ${Math.abs(change)}% de aumento`
        : `⚠️ Tendencia negativa: ${Math.abs(change)}% de disminución`;
      card.appendChild(alert);
    }

    // Funcionalidad de exportación
    exportBtn.addEventListener("click", () => {
      const exportMenu = document.createElement("div");
      exportMenu.style.position = "absolute";
      exportMenu.style.background = "#fff";
      exportMenu.style.border = "1px solid #ccc";
      exportMenu.style.borderRadius = "4px";
      exportMenu.style.padding = "0.5rem";
      exportMenu.style.boxShadow = "0 2px 8px rgba(0,0,0,0.15)";
      exportMenu.style.zIndex = "1000";
      exportMenu.style.minWidth = "120px";
      
      const pngBtn = document.createElement("button");
      pngBtn.className = "btn btn--ghost";
      pngBtn.style.width = "100%";
      pngBtn.style.marginBottom = "0.25rem";
      pngBtn.textContent = "PNG";
      pngBtn.addEventListener("click", () => {
        exportChartAsPNG(svg, title);
        document.body.removeChild(exportMenu);
      });
      
      const svgBtn = document.createElement("button");
      svgBtn.className = "btn btn--ghost";
      svgBtn.style.width = "100%";
      svgBtn.textContent = "SVG";
      svgBtn.addEventListener("click", () => {
        exportChartAsSVG(svg, title);
        document.body.removeChild(exportMenu);
      });
      
      exportMenu.appendChild(pngBtn);
      exportMenu.appendChild(svgBtn);
      
      const rect = exportBtn.getBoundingClientRect();
      exportMenu.style.left = `${rect.left}px`;
      exportMenu.style.top = `${rect.bottom + 5}px`;
      document.body.appendChild(exportMenu);
      
      // Cerrar al hacer clic fuera
      setTimeout(() => {
        const closeMenu = (e) => {
          if (!exportMenu.contains(e.target) && e.target !== exportBtn) {
            if (document.body.contains(exportMenu)) {
              document.body.removeChild(exportMenu);
            }
            document.removeEventListener("click", closeMenu);
          }
        };
        document.addEventListener("click", closeMenu);
      }, 0);
    });

    return card;
  };
  
  // Funciones de exportación
  const exportChartAsPNG = (svg, title) => {
    const svgData = new XMLSerializer().serializeToString(svg);
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const img = new Image();
    
    canvas.width = 800;
    canvas.height = 400;
    
    img.onload = () => {
      ctx.fillStyle = "#fff";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      
      canvas.toBlob((blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${title.replace(/\s+/g, "-")}-${new Date().toISOString().split("T")[0]}.png`;
        a.click();
        URL.revokeObjectURL(url);
      });
    };
    
    img.src = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(svgData)));
  };
  
  const exportChartAsSVG = (svg, title) => {
    const svgData = new XMLSerializer().serializeToString(svg);
    const blob = new Blob([svgData], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title.replace(/\s+/g, "-")}-${new Date().toISOString().split("T")[0]}.svg`;
    a.click();
    URL.revokeObjectURL(url);
  };

  document.getElementById("loadTrendsBtn")?.addEventListener("click", loadTrends);

  // Funcionalidad de filtros avanzados
  const applyFilters = () => {
    const projectId = document.getElementById("dashboardProjectFilter")?.value || "";
    const startDate = document.getElementById("dashboardStartDate")?.value || "";
    const endDate = document.getElementById("dashboardEndDate")?.value || "";
    
    const filters = {};
    if (projectId) filters.project_id = projectId;
    if (startDate) filters.start_date = startDate;
    if (endDate) filters.end_date = endDate;
    
    loadDashboard(filters);
  };

  const resetFilters = () => {
    const projectFilter = document.getElementById("dashboardProjectFilter");
    const startDateInput = document.getElementById("dashboardStartDate");
    const endDateInput = document.getElementById("dashboardEndDate");
    
    if (projectFilter) projectFilter.value = "";
    if (startDateInput) startDateInput.value = "";
    if (endDateInput) endDateInput.value = "";
    
    loadDashboard({});
  };

  // Cargar proyectos al iniciar
  const loadProjectsForFilter = async () => {
    const projectFilter = document.getElementById("dashboardProjectFilter");
    if (!projectFilter) return;
    
    try {
      const response = await fetch("/api/projects/proyectos/?page_size=100");
      if (!response.ok) return;
      const data = await response.json();
      const projects = Array.isArray(data) ? data : (data.results || []);
      
      // Limpiar opciones existentes (excepto "Todos")
      projectFilter.innerHTML = '<option value="">Todos los proyectos</option>';
      
      projects.forEach(project => {
        const option = document.createElement("option");
        option.value = project.id;
        option.textContent = project.name || project.code || `Proyecto ${project.id}`;
        projectFilter.appendChild(option);
      });
    } catch (error) {
      console.error("Error loading projects for filter:", error);
    }
  };

  // Event listeners para filtros
  document.getElementById("dashboardApplyFilters")?.addEventListener("click", applyFilters);
  document.getElementById("dashboardResetFilters")?.addEventListener("click", resetFilters);

  // Cargar proyectos al iniciar
  loadProjectsForFilter();
});
