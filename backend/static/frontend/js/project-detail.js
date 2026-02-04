/**
 * project-detail.js
 * Carga y muestra el detalle de un proyecto
 */

document.addEventListener("DOMContentLoaded", async () => {
  const panel = document.getElementById("projectDetailPanel");
  const projectId = window.projectDetailId;

  if (!panel || !projectId) {
    console.error("[Project Detail] Panel o projectId no encontrado");
    return;
  }

  // Mostrar skeleton mientras carga
  if (window.loadingStates) {
    window.loadingStates.showSkeleton(panel, 1);
  }

  try {
    const response = await fetch(`/api/projects/proyectos/${projectId}/`, {
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }

    const project = await response.json();

    // Renderizar detalle
    renderProjectDetail(panel, project);
  } catch (error) {
    console.error("[Project Detail] Error:", error);
    if (window.loadingStates) {
      window.loadingStates.showError(panel, "Error al cargar el proyecto: " + error.message);
    } else {
      panel.innerHTML = `<div class="panel-title">Error</div><div class="panel-subtitle">${error.message}</div>`;
    }
  }
});

function renderProjectDetail(panel, project) {
  const statusLabels = {
    planning: "Planificación",
    in_progress: "En Progreso",
    on_hold: "En Pausa",
    completed: "Completado",
    cancelled: "Cancelado",
  };

  const priorityLabels = {
    low: "Baja",
    medium: "Media",
    high: "Alta",
    urgent: "Urgente",
  };

  const statusClass = `status-badge status-badge--${project.status}`;
  const priorityClass = `status-badge status-badge--${project.priority}`;

  panel.innerHTML = `
    <div class="panel-title">${project.name || "Sin nombre"}</div>
    <div class="panel-subtitle">Código: ${project.code || "N/A"}</div>
    
    <div class="component-inline" style="margin-top: 1rem; margin-bottom: 1.5rem;">
      <span class="${statusClass}">${statusLabels[project.status] || project.status}</span>
      <span class="${priorityClass}">${priorityLabels[project.priority] || project.priority}</span>
      ${project.progress_pct !== null ? `<span class="helper">Progreso: ${project.progress_pct}%</span>` : ""}
    </div>

    <div class="wizard__section">
      <h3 class="section-title">Información General</h3>
      <div class="field">
        <label class="field-label">Descripción</label>
        <div class="helper">${project.description || "Sin descripción"}</div>
      </div>
      <div class="field">
        <label class="field-label">Dirección del Sitio</label>
        <div class="helper">${project.site_address || "N/A"}</div>
      </div>
      <div class="field">
        <label class="field-label">Cliente</label>
        <div class="helper">${project.client_name || "N/A"}</div>
      </div>
      <div class="field">
        <label class="field-label">Contacto del Cliente</label>
        <div class="helper">${project.client_contact || "N/A"}</div>
      </div>
    </div>

    <div class="wizard__section">
      <h3 class="section-title">Fechas</h3>
      <div class="field">
        <label class="field-label">Fecha de Inicio</label>
        <div class="helper">${project.start_date || "N/A"}</div>
      </div>
      ${project.end_date ? `
      <div class="field">
        <label class="field-label">Fecha de Fin</label>
        <div class="helper">${project.end_date}</div>
      </div>
      ` : ""}
      ${project.estimated_end_date ? `
      <div class="field">
        <label class="field-label">Fecha Estimada de Fin</label>
        <div class="helper">${project.estimated_end_date}</div>
      </div>
      ` : ""}
    </div>

    <div class="wizard__section">
      <h3 class="section-title">Presupuesto</h3>
      ${project.budget_estimated ? `
      <div class="field">
        <label class="field-label">Presupuesto Estimado</label>
        <div class="helper">$${parseFloat(project.budget_estimated).toLocaleString("es-MX", { minimumFractionDigits: 2 })} MXN</div>
      </div>
      ` : ""}
      ${project.budget_actual ? `
      <div class="field">
        <label class="field-label">Presupuesto Actual</label>
        <div class="helper">$${parseFloat(project.budget_actual).toLocaleString("es-MX", { minimumFractionDigits: 2 })} MXN</div>
      </div>
      ` : ""}
    </div>

    <div class="component-inline" id="projectDetailActions" style="margin-top: 1.5rem;">
      <a href="/projects/" class="btn btn--ghost">Volver a Lista</a>
    </div>
  `;

  // Evaluar permisos de edición de forma asíncrona
  if (window.RoleBasedUI) {
    window.RoleBasedUI.getUserContext().then((context) => {
      const canEdit = context?.permissions?.["projects.edit"] || false;
      if (canEdit) {
        const actionsDiv = document.getElementById("projectDetailActions");
        if (actionsDiv) {
          const editBtn = document.createElement("a");
          editBtn.href = `/projects/${project.id}/edit/`;
          editBtn.className = "btn btn--primary";
          editBtn.textContent = "Editar";
          actionsDiv.insertBefore(editBtn, actionsDiv.firstChild);
        }
      }
    });
  }
}
