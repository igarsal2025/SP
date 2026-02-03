/**
 * project-edit.js
 * Carga y permite editar un proyecto
 */

document.addEventListener("DOMContentLoaded", async () => {
  const panel = document.getElementById("projectEditPanel");
  const projectId = window.projectEditId;

  if (!panel || !projectId) {
    console.error("[Project Edit] Panel o projectId no encontrado");
    return;
  }

  // Mostrar skeleton mientras carga
  if (window.loadingStates) {
    window.loadingStates.showSkeleton(panel, 1);
  }

  try {
    // Cargar proyecto
    const response = await fetch(`/api/projects/proyectos/${projectId}/`, {
      credentials: "include",
    });

    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }

    const project = await response.json();

    // Renderizar formulario de edición
    renderProjectEditForm(panel, project);
  } catch (error) {
    console.error("[Project Edit] Error:", error);
    if (window.loadingStates) {
      window.loadingStates.showError(panel, "Error al cargar el proyecto: " + error.message);
    } else {
      panel.innerHTML = `<div class="panel-title">Error</div><div class="panel-subtitle">${error.message}</div>`;
    }
  }
});

function renderProjectEditForm(panel, project) {
  panel.innerHTML = `
    <div class="panel-title">Editar Proyecto</div>
    <div class="panel-subtitle">${project.name || "Sin nombre"}</div>
    
    <form id="projectEditForm" class="wizard__form">
      <div class="field">
        <label class="field-label" for="projectName">Nombre del Proyecto *</label>
        <input class="input" type="text" id="projectName" name="name" value="${escapeHtml(project.name || "")}" required />
      </div>
      <div class="field">
        <label class="field-label" for="projectCode">Código del Proyecto *</label>
        <input class="input" type="text" id="projectCode" name="code" value="${escapeHtml(project.code || "")}" required />
      </div>
      <div class="field">
        <label class="field-label" for="projectDescription">Descripción</label>
        <textarea class="input" id="projectDescription" name="description" rows="3">${escapeHtml(project.description || "")}</textarea>
      </div>
      <div class="field">
        <label class="field-label" for="projectSiteAddress">Dirección del Sitio *</label>
        <textarea class="input" id="projectSiteAddress" name="site_address" rows="2" required>${escapeHtml(project.site_address || "")}</textarea>
      </div>
      <div class="field">
        <label class="field-label" for="projectClientName">Nombre del Cliente</label>
        <input class="input" type="text" id="projectClientName" name="client_name" value="${escapeHtml(project.client_name || "")}" />
      </div>
      <div class="field">
        <label class="field-label" for="projectClientContact">Contacto del Cliente</label>
        <input class="input" type="text" id="projectClientContact" name="client_contact" value="${escapeHtml(project.client_contact || "")}" />
      </div>
      <div class="field">
        <label class="field-label" for="projectStartDate">Fecha de Inicio *</label>
        <input class="input" type="date" id="projectStartDate" name="start_date" value="${project.start_date || ""}" required />
      </div>
      <div class="field">
        <label class="field-label" for="projectEndDate">Fecha de Fin</label>
        <input class="input" type="date" id="projectEndDate" name="end_date" value="${project.end_date || ""}" />
      </div>
      <div class="field">
        <label class="field-label" for="projectEstimatedEndDate">Fecha Estimada de Fin</label>
        <input class="input" type="date" id="projectEstimatedEndDate" name="estimated_end_date" value="${project.estimated_end_date || ""}" />
      </div>
      <div class="field">
        <label class="field-label" for="projectStatus">Estado *</label>
        <select class="input" id="projectStatus" name="status" required>
          <option value="planning" ${project.status === "planning" ? "selected" : ""}>Planificación</option>
          <option value="in_progress" ${project.status === "in_progress" ? "selected" : ""}>En Progreso</option>
          <option value="on_hold" ${project.status === "on_hold" ? "selected" : ""}>En Pausa</option>
          <option value="completed" ${project.status === "completed" ? "selected" : ""}>Completado</option>
          <option value="cancelled" ${project.status === "cancelled" ? "selected" : ""}>Cancelado</option>
        </select>
      </div>
      <div class="field">
        <label class="field-label" for="projectPriority">Prioridad *</label>
        <select class="input" id="projectPriority" name="priority" required>
          <option value="low" ${project.priority === "low" ? "selected" : ""}>Baja</option>
          <option value="medium" ${project.priority === "medium" ? "selected" : ""}>Media</option>
          <option value="high" ${project.priority === "high" ? "selected" : ""}>Alta</option>
          <option value="urgent" ${project.priority === "urgent" ? "selected" : ""}>Urgente</option>
        </select>
      </div>
      <div class="field">
        <label class="field-label" for="projectProgress">Progreso (%)</label>
        <input class="input" type="number" id="projectProgress" name="progress_pct" min="0" max="100" value="${project.progress_pct || 0}" />
      </div>
      <div class="field">
        <label class="field-label" for="projectBudgetEstimated">Presupuesto Estimado (MXN)</label>
        <input class="input" type="number" id="projectBudgetEstimated" name="budget_estimated" step="0.01" min="0" value="${project.budget_estimated || ""}" />
      </div>
      <div class="field">
        <label class="field-label" for="projectBudgetActual">Presupuesto Actual (MXN)</label>
        <input class="input" type="number" id="projectBudgetActual" name="budget_actual" step="0.01" min="0" value="${project.budget_actual || ""}" />
      </div>
      <div class="component-inline" style="margin-top: 1.5rem;">
        <button class="btn btn--primary" type="submit">Guardar Cambios</button>
        <a href="/projects/${project.id}/" class="btn btn--ghost">Cancelar</a>
      </div>
    </form>
  `;

  // Agregar handler de submit
  const form = document.getElementById("projectEditForm");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      await saveProject(project.id, form);
    });
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

async function saveProject(projectId, form) {
  const formData = new FormData(form);
  const data = {};
  formData.forEach((value, key) => {
    if (value) {
      data[key] = value;
    }
  });

  // Convertir números
  if (data.progress_pct) data.progress_pct = parseInt(data.progress_pct, 10);
  if (data.budget_estimated) data.budget_estimated = parseFloat(data.budget_estimated);
  if (data.budget_actual) data.budget_actual = parseFloat(data.budget_actual);

  const submitBtn = form.querySelector('button[type="submit"]');
  if (window.loadingStates) {
    window.loadingStates.setButtonLoading(submitBtn, true);
  }

  try {
    const response = await fetch(`/api/projects/proyectos/${projectId}/`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || error.message || "Error al guardar");
    }

    if (window.loadingStates) {
      window.loadingStates.showSuccess(form, "Proyecto actualizado correctamente");
    }

    // Redirigir a detalle después de 1 segundo
    setTimeout(() => {
      window.location.href = `/projects/${projectId}/`;
    }, 1000);
  } catch (error) {
    console.error("[Project Edit] Error al guardar:", error);
    if (window.loadingStates) {
      window.loadingStates.showError(form, "Error al guardar: " + error.message);
    } else {
      alert("Error al guardar: " + error.message);
    }
  } finally {
    if (window.loadingStates && submitBtn) {
      window.loadingStates.setButtonLoading(submitBtn, false);
    }
  }
}
