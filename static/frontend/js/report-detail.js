/**
 * report-detail.js
 * Carga y muestra el detalle de un reporte
 */

document.addEventListener("DOMContentLoaded", async () => {
  const panel = document.getElementById("reportDetailPanel");
  const reportId = window.reportDetailId;

  if (!panel || !reportId) {
    console.error("[Report Detail] Panel o reportId no encontrado");
    return;
  }

  // Mostrar skeleton mientras carga
  if (window.loadingStates) {
    window.loadingStates.showSkeleton(panel, 1);
  }

  try {
    const response = await fetch(`/api/reports/reportes/${reportId}/`, {
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }

    const report = await response.json();

    // Renderizar detalle
    renderReportDetail(panel, report);
  } catch (error) {
    console.error("[Report Detail] Error:", error);
    if (window.loadingStates) {
      window.loadingStates.showError(panel, "Error al cargar el reporte: " + error.message);
    } else {
      panel.innerHTML = `<div class="panel-title">Error</div><div class="panel-subtitle">${error.message}</div>`;
    }
  }
});

function renderReportDetail(panel, report) {
  const statusLabels = {
    draft: "Borrador",
    submitted: "Enviado",
    approved: "Aprobado",
    rejected: "Rechazado",
  };

  const statusClass = `status-badge status-badge--${report.status}`;

  panel.innerHTML = `
    <div class="panel-title">${report.project_name || "Sin nombre"}</div>
    <div class="panel-subtitle">Semana: ${report.week_start || "N/A"}</div>
    
    <div class="component-inline" style="margin-top: 1rem; margin-bottom: 1.5rem;">
      <span class="${statusClass}">${statusLabels[report.status] || report.status}</span>
      ${report.progress_pct !== null ? `<span class="helper">Progreso: ${report.progress_pct}%</span>` : ""}
    </div>

    <div class="wizard__section">
      <h3 class="section-title">Información General</h3>
      <div class="field">
        <label class="field-label">Dirección del Sitio</label>
        <div class="helper">${report.site_address || "N/A"}</div>
      </div>
      <div class="field">
        <label class="field-label">Técnico</label>
        <div class="helper">${report.technician || "N/A"}</div>
      </div>
      ${report.supervisor ? `
      <div class="field">
        <label class="field-label">Supervisor</label>
        <div class="helper">${report.supervisor}</div>
      </div>
      ` : ""}
    </div>

    <div class="wizard__section">
      <h3 class="section-title">Datos Técnicos</h3>
      ${report.cabling_nodes_total !== null ? `
      <div class="field">
        <label class="field-label">Nodos Cableados (Total)</label>
        <div class="helper">${report.cabling_nodes_total}</div>
      </div>
      ` : ""}
      ${report.cabling_nodes_ok !== null ? `
      <div class="field">
        <label class="field-label">Nodos Cableados (OK)</label>
        <div class="helper">${report.cabling_nodes_ok}</div>
      </div>
      ` : ""}
      ${report.racks_installed !== null ? `
      <div class="field">
        <label class="field-label">Racks Instalados</label>
        <div class="helper">${report.racks_installed}</div>
      </div>
      ` : ""}
      ${report.security_devices !== null ? `
      <div class="field">
        <label class="field-label">Dispositivos de Seguridad</label>
        <div class="helper">${report.security_devices}</div>
      </div>
      ` : ""}
      ${report.materials_count !== null ? `
      <div class="field">
        <label class="field-label">Materiales</label>
        <div class="helper">${report.materials_count}</div>
      </div>
      ` : ""}
    </div>

    ${report.incidents ? `
    <div class="wizard__section">
      <h3 class="section-title">Incidentes</h3>
      <div class="field">
        <label class="field-label">Cantidad de Incidentes</label>
        <div class="helper">${report.incidents_count || 0}</div>
      </div>
      ${report.incidents_severity ? `
      <div class="field">
        <label class="field-label">Severidad</label>
        <div class="helper">${report.incidents_severity}</div>
      </div>
      ` : ""}
      ${report.incidents_detail ? `
      <div class="field">
        <label class="field-label">Detalle</label>
        <div class="helper">${report.incidents_detail}</div>
      </div>
      ` : ""}
      ${report.mitigation_plan ? `
      <div class="field">
        <label class="field-label">Plan de Mitigación</label>
        <div class="helper">${report.mitigation_plan}</div>
      </div>
      ` : ""}
    </div>
    ` : ""}

    <div class="wizard__section">
      <h3 class="section-title">Fechas</h3>
      ${report.created_at ? `
      <div class="field">
        <label class="field-label">Creado</label>
        <div class="helper">${new Date(report.created_at).toLocaleString("es-MX")}</div>
      </div>
      ` : ""}
      ${report.submitted_at ? `
      <div class="field">
        <label class="field-label">Enviado</label>
        <div class="helper">${new Date(report.submitted_at).toLocaleString("es-MX")}</div>
      </div>
      ` : ""}
      ${report.approved_at ? `
      <div class="field">
        <label class="field-label">Aprobado</label>
        <div class="helper">${new Date(report.approved_at).toLocaleString("es-MX")}</div>
      </div>
      ` : ""}
      ${report.rejected_at ? `
      <div class="field">
        <label class="field-label">Rechazado</label>
        <div class="helper">${new Date(report.rejected_at).toLocaleString("es-MX")}</div>
      </div>
      ` : ""}
    </div>

    <div class="component-inline" style="margin-top: 1.5rem;">
      <a href="/reports/" class="btn btn--ghost">Volver a Lista</a>
    </div>
  `;
}
