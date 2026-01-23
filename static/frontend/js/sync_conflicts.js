/**
 * Módulo para resolución avanzada de conflictos con diffs visuales
 */

class ConflictResolver {
  constructor(sessionId) {
    this.sessionId = sessionId;
  }

  /**
   * Obtener diff visual de un conflicto
   */
  async getDiff(itemId, clientData = null) {
    try {
      const params = new URLSearchParams();
      if (clientData) {
        params.set("client_data", JSON.stringify(clientData));
      }
      
      const response = await fetch(
        `/api/sync/sessions/${this.sessionId}/conflicts/${itemId}/diff/?${params.toString()}`
      );
      
      if (!response.ok) {
        throw new Error(`Error al obtener diff: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error("Error obteniendo diff:", error);
      throw error;
    }
  }

  /**
   * Resolver conflicto con resolución granular
   */
  async resolveConflict(itemId, resolution, clientData) {
    try {
      const response = await fetch(
        `/api/sync/sessions/${this.sessionId}/conflicts/${itemId}/resolve/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            resolution: resolution, // { "field_name": "server"|"client"|"merge" }
            client_data: clientData
          })
        }
      );
      
      if (!response.ok) {
        throw new Error(`Error al resolver conflicto: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error("Error resolviendo conflicto:", error);
      throw error;
    }
  }

  /**
   * Renderizar diff visual en el DOM
   */
  renderDiff(container, diffData) {
    const { diff, server_data, client_data, entity_type, entity_id } = diffData;
    
    container.innerHTML = "";
    
    // Header
    const header = document.createElement("div");
    header.className = "conflict-header";
    header.innerHTML = `
      <h3>Conflicto: ${entity_type} - ${entity_id}</h3>
      <p class="helper">Selecciona qué versión usar para cada campo</p>
    `;
    container.appendChild(header);
    
    // Campos modificados
    if (Object.keys(diff.modified).length > 0) {
      const modifiedSection = this._createSection("Campos Modificados", "modified");
      Object.entries(diff.modified).forEach(([field, values]) => {
        modifiedSection.appendChild(
          this._createFieldDiff(field, values, "modified")
        );
      });
      container.appendChild(modifiedSection);
    }
    
    // Campos agregados
    if (Object.keys(diff.added).length > 0) {
      const addedSection = this._createSection("Campos Agregados (solo en cliente)", "added");
      Object.entries(diff.added).forEach(([field, values]) => {
        addedSection.appendChild(
          this._createFieldDiff(field, values, "added")
        );
      });
      container.appendChild(addedSection);
    }
    
    // Campos removidos
    if (Object.keys(diff.removed).length > 0) {
      const removedSection = this._createSection("Campos Removidos (solo en servidor)", "removed");
      Object.entries(diff.removed).forEach(([field, values]) => {
        removedSection.appendChild(
          this._createFieldDiff(field, values, "removed")
        );
      });
      container.appendChild(removedSection);
    }
    
    // Botones de acción
    const actions = document.createElement("div");
    actions.className = "component-inline";
    actions.style.marginTop = "20px";
    
    const resolveBtn = document.createElement("button");
    resolveBtn.className = "btn btn--primary";
    resolveBtn.textContent = "Resolver Conflicto";
    resolveBtn.addEventListener("click", () => this._handleResolve(container, diffData));
    actions.appendChild(resolveBtn);
    
    const cancelBtn = document.createElement("button");
    cancelBtn.className = "btn btn--ghost";
    cancelBtn.textContent = "Cancelar";
    cancelBtn.addEventListener("click", () => container.innerHTML = "");
    actions.appendChild(cancelBtn);
    
    container.appendChild(actions);
  }

  _createSection(title, type) {
    const section = document.createElement("div");
    section.className = "wizard__panel";
    section.dataset.diffType = type;
    
    const titleEl = document.createElement("div");
    titleEl.className = "panel-title";
    titleEl.textContent = title;
    section.appendChild(titleEl);
    
    return section;
  }

  _createFieldDiff(field, values, type) {
    const fieldDiv = document.createElement("div");
    fieldDiv.className = "field-diff";
    fieldDiv.dataset.field = field;
    
    const label = document.createElement("label");
    label.className = "helper";
    label.textContent = this._formatFieldName(field);
    fieldDiv.appendChild(label);
    
    // Versión servidor
    const serverDiv = document.createElement("div");
    serverDiv.className = "diff-version diff-server";
    serverDiv.innerHTML = `
      <div class="diff-version__header">
        <strong>Servidor</strong>
        <button class="btn btn--small btn--ghost" data-action="use-server" data-field="${field}">
          Usar esta
        </button>
      </div>
      <div class="diff-version__content">
        <pre>${this._formatValue(values.server)}</pre>
      </div>
    `;
    fieldDiv.appendChild(serverDiv);
    
    // Versión cliente
    if (values.client !== null) {
      const clientDiv = document.createElement("div");
      clientDiv.className = "diff-version diff-client";
      clientDiv.innerHTML = `
        <div class="diff-version__header">
          <strong>Cliente</strong>
          <button class="btn btn--small btn--ghost" data-action="use-client" data-field="${field}">
            Usar esta
          </button>
        </div>
        <div class="diff-version__content">
          <pre>${this._formatValue(values.client)}</pre>
        </div>
      `;
      fieldDiv.appendChild(clientDiv);
    }
    
    // Opción de merge (si aplica)
    if (type === "modified" && this._canMerge(values.server, values.client)) {
      const mergeBtn = document.createElement("button");
      mergeBtn.className = "btn btn--small btn--ghost";
      mergeBtn.textContent = "Combinar (merge)";
      mergeBtn.dataset.action = "use-merge";
      mergeBtn.dataset.field = field;
      mergeBtn.style.marginTop = "10px";
      fieldDiv.appendChild(mergeBtn);
    }
    
    // Radio buttons para selección
    const radioDiv = document.createElement("div");
    radioDiv.className = "diff-radio-group";
    radioDiv.innerHTML = `
      <label>
        <input type="radio" name="diff_${field}" value="server" checked>
        Servidor
      </label>
      <label>
        <input type="radio" name="diff_${field}" value="client">
        Cliente
      </label>
      ${this._canMerge(values.server, values.client) ? `
        <label>
          <input type="radio" name="diff_${field}" value="merge">
          Combinar
        </label>
      ` : ''}
    `;
    fieldDiv.appendChild(radioDiv);
    
    return fieldDiv;
  }

  _formatFieldName(field) {
    return field.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
  }

  _formatValue(value) {
    if (value === null || value === undefined) {
      return "(vacío)";
    }
    if (typeof value === "object") {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  }

  _canMerge(serverValue, clientValue) {
    return (
      (typeof serverValue === "object" && typeof clientValue === "object") ||
      (Array.isArray(serverValue) && Array.isArray(clientValue))
    );
  }

  async _handleResolve(container, diffData) {
    const resolution = {};
    
    // Recopilar resoluciones de radio buttons
    container.querySelectorAll("[name^='diff_']").forEach(radio => {
      const field = radio.name.replace("diff_", "");
      if (radio.checked) {
        resolution[field] = radio.value;
      }
    });
    
    if (Object.keys(resolution).length === 0) {
      alert("Por favor selecciona una resolución para al menos un campo");
      return;
    }
    
    try {
      const result = await this.resolveConflict(
        diffData.entity_id,
        resolution,
        diffData.client_data
      );
      
      // Mostrar éxito
      container.innerHTML = `
        <div class="status" data-level="success">
          Conflicto resuelto exitosamente
        </div>
      `;
      
      // Disparar evento
      container.dispatchEvent(new CustomEvent("conflict:resolved", {
        detail: result
      }));
    } catch (error) {
      container.innerHTML = `
        <div class="status" data-level="error">
          Error al resolver conflicto: ${error.message}
        </div>
      `;
    }
  }
}

// Exportar para uso global
window.ConflictResolver = ConflictResolver;
