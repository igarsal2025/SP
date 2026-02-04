/**
 * project-create.js
 * Maneja la creación de nuevos proyectos
 */

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("projectCreateForm");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    await createProject(form);
  });
});

async function createProject(form) {
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

  const submitBtn = form.querySelector('button[type="submit"]');
  if (window.loadingStates) {
    window.loadingStates.setButtonLoading(submitBtn, true);
  }

  try {
    const response = await fetch("/api/projects/proyectos/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || error.message || "Error al crear proyecto");
    }

    const project = await response.json();

    if (window.loadingStates) {
      window.loadingStates.showSuccess(form, "Proyecto creado correctamente");
    }

    // Redirigir a detalle después de 1 segundo
    setTimeout(() => {
      window.location.href = `/projects/${project.id}/`;
    }, 1000);
  } catch (error) {
    console.error("[Project Create] Error:", error);
    if (window.loadingStates) {
      window.loadingStates.showError(form, "Error al crear: " + error.message);
    } else {
      alert("Error al crear proyecto: " + error.message);
    }
  } finally {
    if (window.loadingStates && submitBtn) {
      window.loadingStates.setButtonLoading(submitBtn, false);
    }
  }
}
