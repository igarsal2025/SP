(() => {
  const FIELD_LABELS = {
    project_name: "Nombre del proyecto",
    project_code: "Codigo de proyecto",
    week_start: "Inicio de semana",
    site_address: "Direccion del sitio",
    site_city: "Ciudad",
    site_state: "Estado",
    technician: "Tecnico responsable",
    client_name: "Cliente",
    site_contact: "Contacto en sitio",
    initial_notes: "Notas iniciales",
    progress_pct: "% avance",
    schedule_status: "Estado de calendario",
    planned_start: "Inicio planificado",
    planned_end: "Fin planificado",
    actual_start: "Inicio real",
    actual_end: "Fin real",
    risks_summary: "Riesgos o bloqueos",
    cabling_nodes_total: "Total nodos cableados",
    cabling_nodes_ok: "Nodos OK",
    cable_type: "Tipo de cable",
    cable_length_m: "Longitud instalada (m)",
    cable_trays_ok: "Canaletas OK",
    labeling_ok: "Etiquetado OK",
    racks_installed: "Racks instalados",
    rack_order_ok: "Orden correcto",
    rack_units_used: "Unidades usadas (U)",
    cooling_ok: "Enfriamiento OK",
    power_ok: "Energia OK",
    security_devices: "Dispositivos de seguridad",
    cameras_online: "Camaras online",
    camera_count: "Total camaras",
    access_control_count: "Control de acceso",
    av_systems_count: "Sistemas AV",
    security_notes: "Observaciones de seguridad",
    special_systems_enabled: "Sistemas especializados habilitados",
    special_systems_type: "Tipo de sistema",
    special_systems_vendor: "Proveedor",
    special_systems_integration_ok: "Integracion completa",
    special_systems_notes: "Notas sistemas especializados",
    materials_count: "Total materiales",
    tools_used: "Herramientas usadas",
    missing_materials: "Faltantes",
    missing_materials_detail: "Detalle faltantes",
    materials_list: "Lista de materiales",
    tests_passed: "Pruebas aprobadas",
    qa_signed: "QA firmado",
    test_notes: "Notas de pruebas",
    evidence_photos: "Evidencias (URLs o IDs)",
    evidence_geo: "Geolocalizacion evidencias",
    evidence_ids: "IDs de evidencia",
    evidence_notes: "Notas de evidencia",
    incidents: "Incidentes (si/no)",
    incidents_severity: "Severidad",
    incidents_count: "Numero de incidentes",
    incidents_detail: "Detalle de incidentes",
    mitigation_plan: "Plan de mitigacion",
    signature_tech: "Firma tecnico",
    signature_supervisor_required: "Requiere firma supervisor",
    signature_supervisor: "Firma supervisor",
    signature_client: "Firma cliente",
    signature_method: "Metodo de firma",
    signature_date: "Fecha de firma",
    report_summary: "Resumen final",
    next_actions: "Proximas acciones",
    final_review_ack: "Confirmo revision final",
    client_feedback: "Feedback del cliente",
  };

  const COMPONENT_CONTRACTS = {
    riskMatrix: {
      input: {
        project_id: "UUID",
        riesgos: [
          {
            id: "UUID",
            title: "string",
            severity: "low|medium|high|critical",
            probability: "very_low|low|medium|high|very_high",
          },
        ],
      },
      output: {
        levels: ["Muy baja", "Baja", "Media", "Alta", "Muy alta"],
        matrix: "5x5 con conteos por celda",
      },
    },
    ganttLite: {
      input: {
        project_id: "UUID",
        tareas: [{ id: "UUID", title: "string", status: "pending|in_progress|completed|blocked" }],
      },
      output: {
        rows: [{ name: "string", progress: "0-100" }],
      },
    },
    kanban: {
      input: {
        project_id: "UUID",
        tareas: [{ id: "UUID", title: "string", status: "pending|in_progress|completed|blocked" }],
      },
      output: {
        columns: ["Pendiente", "En progreso", "Hecho", "Bloqueado"],
      },
    },
  };

  function setComponentState(wrapper, state, statusEl, message) {
    if (wrapper) {
      wrapper.dataset.state = state;
    }
    if (statusEl && message !== undefined) {
      statusEl.textContent = message;
    }
  }

  function labelFromName(name) {
    if (FIELD_LABELS[name]) return FIELD_LABELS[name];
    return name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  }

  function applyShowRules(element, field) {
    if (field.required_if) {
      element.dataset.showRule = JSON.stringify({
        mode: "all",
        conditions: Object.entries(field.required_if).map(([dep, value]) => ({
          field: dep,
          value,
        })),
      });
    }
    if (field.show_if) {
      element.dataset.showRule = JSON.stringify({
        mode: "all",
        conditions: Object.entries(field.show_if).map(([dep, value]) => ({
          field: dep,
          value,
        })),
      });
    }
    if (field.show_if_any) {
      element.dataset.showRule = JSON.stringify({
        mode: "any",
        conditions: field.show_if_any || [],
      });
    }
    if (field.show_if_all) {
      element.dataset.showRule = JSON.stringify({
        mode: "all",
        conditions: field.show_if_all || [],
      });
    }
  }

  function applyRequiredRules(input, field) {
    if (field.required) {
      input.setAttribute("aria-required", "true");
    }
    if (field.required_if) {
      input.dataset.requiredRule = JSON.stringify({
        mode: "all",
        conditions: Object.entries(field.required_if).map(([dep, value]) => ({
          field: dep,
          value,
        })),
      });
    }
    if (field.required_if_any) {
      input.dataset.requiredRule = JSON.stringify({
        mode: "any",
        conditions: field.required_if_any || [],
      });
    }
    if (field.required_if_all) {
      input.dataset.requiredRule = JSON.stringify({
        mode: "all",
        conditions: field.required_if_all || [],
      });
    }
  }

  function createInputControl(field) {
    let input;
    if (field.type === "textarea") {
      input = document.createElement("textarea");
      input.className = "input input--textarea";
    } else if (field.type === "select") {
      input = document.createElement("select");
      input.className = "input";
      const empty = document.createElement("option");
      empty.value = "";
      empty.textContent = "Seleccionar";
      input.appendChild(empty);
      (field.options || []).forEach((option) => {
        const opt = document.createElement("option");
        opt.value = option;
        opt.textContent =
          option === "true"
            ? "Si"
            : option === "false"
            ? "No"
            : option === "low"
            ? "Baja"
            : option === "medium"
            ? "Media"
            : option === "high"
            ? "Alta"
            : option;
        input.appendChild(opt);
      });
    } else {
      input = document.createElement("input");
      input.className = "input";
      input.type = field.type || "text";
    }

    input.name = field.name;
    input.setAttribute("data-autosave", "");
    applyRequiredRules(input, field);
    if (field.min !== undefined) input.setAttribute("min", field.min);
    if (field.max !== undefined) input.setAttribute("max", field.max);
    if (field.regex) input.setAttribute("pattern", field.regex);
    return input;
  }

  function createField(field) {
    const label = document.createElement("label");
    label.className = "field";
    applyShowRules(label, field);

    const title = document.createElement("span");
    title.textContent = labelFromName(field.name);
    label.appendChild(title);

    const input = createInputControl(field);
    label.appendChild(input);

    return label;
  }

  function createSignaturePad(targetInput, labelText, options = {}) {
    const wrapper = document.createElement("div");
    wrapper.className = "signature-pad";
    wrapper.dataset.component = "signature-pad";
    const dateInput = options.dateInput || null;
    const methodInput = options.methodInput || null;
    const methodValue = options.methodValue || "canvas";
    const exportName = options.exportName || targetInput.name || "firma";
    const readOnly = options.readOnly === true;
    const label = document.createElement("div");
    label.className = "panel-title";
    label.textContent = labelText;
    const status = document.createElement("div");
    status.className = "helper";
    status.textContent = "Sin firma";
    const canvas = document.createElement("canvas");
    canvas.width = 360;
    canvas.height = 120;
    canvas.className = "signature-pad__canvas";
    const actions = document.createElement("div");
    actions.className = "component-inline";
    const clearBtn = document.createElement("button");
    clearBtn.type = "button";
    clearBtn.className = "btn btn--ghost";
    clearBtn.textContent = "Limpiar";
    const saveBtn = document.createElement("button");
    saveBtn.type = "button";
    saveBtn.className = "btn btn--secondary";
    saveBtn.textContent = "Guardar firma";
    const downloadBtn = document.createElement("button");
    downloadBtn.type = "button";
    downloadBtn.className = "btn btn--ghost";
    downloadBtn.textContent = "Descargar firma";
    downloadBtn.disabled = true;
    actions.appendChild(clearBtn);
    actions.appendChild(saveBtn);
    actions.appendChild(downloadBtn);

    let drawing = false;
    const ctx = canvas.getContext("2d");
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    ctx.strokeStyle = "#111827";

    const getPos = (evt) => {
      const rect = canvas.getBoundingClientRect();
      const clientX = evt.touches ? evt.touches[0].clientX : evt.clientX;
      const clientY = evt.touches ? evt.touches[0].clientY : evt.clientY;
      return { x: clientX - rect.left, y: clientY - rect.top };
    };

    const start = (evt) => {
      drawing = true;
      const pos = getPos(evt);
      ctx.beginPath();
      ctx.moveTo(pos.x, pos.y);
    };

    const move = (evt) => {
      if (!drawing) return;
      const pos = getPos(evt);
      ctx.lineTo(pos.x, pos.y);
      ctx.stroke();
    };

    const stop = () => {
      drawing = false;
    };

    const hasInk = () => {
      const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
      for (let i = 3; i < pixels.length; i += 4) {
        if (pixels[i] !== 0) return true;
      }
      return false;
    };

    if (!readOnly) {
      canvas.addEventListener("mousedown", start);
      canvas.addEventListener("mousemove", move);
      canvas.addEventListener("mouseup", stop);
      canvas.addEventListener("mouseleave", stop);
      canvas.addEventListener("touchstart", start, { passive: true });
      canvas.addEventListener("touchmove", move, { passive: true });
      canvas.addEventListener("touchend", stop);
    } else {
      canvas.style.pointerEvents = "none";
    }

    const formatDateValue = (input) => {
      if (!input) return null;
      const now = new Date();
      if (input.type === "date") {
        return now.toISOString().slice(0, 10);
      }
      if (input.type === "datetime-local") {
        const local = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
        return local.toISOString().slice(0, 16);
      }
      return now.toISOString();
    };

    clearBtn.addEventListener("click", () => {
      if (readOnly) return;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      targetInput.value = "";
      targetInput.dispatchEvent(new Event("change"));
      if (dateInput && dateInput.value) {
        dateInput.value = "";
        dateInput.dispatchEvent(new Event("change"));
      }
      if (methodInput && methodInput.value) {
        methodInput.value = "";
        methodInput.dispatchEvent(new Event("change"));
      }
      downloadBtn.disabled = true;
      setComponentState(wrapper, "empty", status, "Sin firma");
    });

    saveBtn.addEventListener("click", () => {
      if (readOnly) return;
      if (!hasInk()) {
        targetInput.value = "";
        targetInput.dispatchEvent(new Event("change"));
        downloadBtn.disabled = true;
        setComponentState(wrapper, "empty", status, "Firma vacia");
        return;
      }
      const dataUrl = canvas.toDataURL("image/png");
      targetInput.value = dataUrl;
      targetInput.dispatchEvent(new Event("change"));
      if (dateInput && !dateInput.value) {
        const dateValue = formatDateValue(dateInput);
        if (dateValue) {
          dateInput.value = dateValue;
        }
        dateInput.dispatchEvent(new Event("change"));
      }
      if (methodInput && !methodInput.value) {
        methodInput.value = methodValue;
        methodInput.dispatchEvent(new Event("change"));
      }
      downloadBtn.disabled = false;
      setComponentState(wrapper, "ready", status, "Firma guardada");
    });

    downloadBtn.addEventListener("click", () => {
      if (!targetInput.value) return;
      const link = document.createElement("a");
      link.href = targetInput.value;
      link.download = `${exportName}.png`;
      link.click();
    });

    if (targetInput.value && targetInput.value.startsWith("data:image")) {
      const img = new Image();
      img.onload = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      };
      img.src = targetInput.value;
      downloadBtn.disabled = false;
      setComponentState(wrapper, "ready", status, "Firma cargada");
    } else {
      setComponentState(wrapper, "empty", status, readOnly ? "Pendiente de firma" : "Sin firma");
    }

    if (readOnly) {
      clearBtn.disabled = true;
      saveBtn.disabled = true;
      wrapper.dataset.state = "readonly";
    }

    wrapper.appendChild(label);
    wrapper.appendChild(status);
    wrapper.appendChild(canvas);
    wrapper.appendChild(actions);
    return wrapper;
  }

  function createEvidenceUploader(targetInput) {
    const wrapper = document.createElement("div");
    wrapper.className = "evidence-uploader";
    wrapper.dataset.component = "evidence-uploader";
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "image/*";
    input.multiple = true;
    input.className = "input";
    const status = document.createElement("div");
    status.className = "helper";
    const list = document.createElement("div");
    list.className = "evidence-uploader__list";
    const previews = document.createElement("div");
    previews.className = "evidence-uploader__previews";
    const clearBtn = document.createElement("button");
    clearBtn.type = "button";
    clearBtn.className = "btn btn--ghost";
    clearBtn.textContent = "Limpiar evidencias";
    let previewUrls = [];

    const renderList = (files) => {
      list.innerHTML = "";
      previews.innerHTML = "";
      previewUrls.forEach((url) => URL.revokeObjectURL(url));
      previewUrls = [];
      if (!files.length) {
        const empty = document.createElement("div");
        empty.className = "component-empty";
        empty.textContent = "Sin evidencias cargadas.";
        list.appendChild(empty);
        setComponentState(wrapper, "empty", status, "Sin evidencias");
        return;
      }
      setComponentState(wrapper, "ready", status, `${files.length} evidencia(s)`);
      files.forEach((file) => {
        const item = document.createElement("div");
        item.textContent = file.name;
        list.appendChild(item);
        const preview = document.createElement("img");
        const url = URL.createObjectURL(file);
        previewUrls.push(url);
        preview.src = url;
        preview.alt = file.name;
        preview.className = "evidence-uploader__preview";
        previews.appendChild(preview);
      });
    };

    input.addEventListener("change", () => {
      const files = Array.from(input.files || []);
      renderList(files);
      targetInput.value = files.map((file) => file.name).join("; ");
      targetInput.dispatchEvent(new Event("change"));
    });

    clearBtn.addEventListener("click", () => {
      input.value = "";
      targetInput.value = "";
      renderList([]);
      targetInput.dispatchEvent(new Event("change"));
    });

    wrapper.appendChild(input);
    wrapper.appendChild(status);
    wrapper.appendChild(list);
    wrapper.appendChild(previews);
    wrapper.appendChild(clearBtn);
    renderList([]);
    return wrapper;
  }

  function createGeoPicker(targetInput) {
    const wrapper = document.createElement("div");
    wrapper.className = "geo-picker";
    wrapper.dataset.component = "geo-picker";
    const button = document.createElement("button");
    button.type = "button";
    button.className = "btn btn--ghost";
    button.textContent = "Usar ubicacion actual";
    const status = document.createElement("div");
    status.className = "helper";
    status.textContent = "Sin ubicacion";
    setComponentState(wrapper, "empty", status, "Sin ubicacion");

    button.addEventListener("click", () => {
      if (!navigator.geolocation) {
        setComponentState(wrapper, "error", status, "Geolocalizacion no disponible");
        return;
      }
      setComponentState(wrapper, "loading", status, "Obteniendo ubicacion...");
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const value = `${pos.coords.latitude},${pos.coords.longitude}`;
          targetInput.value = value;
          targetInput.dispatchEvent(new Event("change"));
          setComponentState(wrapper, "ready", status, `Ubicacion: ${value}`);
        },
        () => {
          setComponentState(wrapper, "error", status, "No se pudo obtener ubicacion");
        },
        { enableHighAccuracy: false, timeout: 6000, maximumAge: 600000 }
      );
    });

    if (targetInput.value) {
      setComponentState(wrapper, "ready", status, `Ubicacion: ${targetInput.value}`);
    }

    wrapper.appendChild(button);
    wrapper.appendChild(status);
    return wrapper;
  }

  function renderEmptyState(message) {
    const empty = document.createElement("div");
    empty.className = "component-empty";
    empty.textContent = message;
    return empty;
  }

  function buildRiskMatrixFromRisks(risks) {
    const probabilityIndex = {
      very_low: 0,
      low: 1,
      medium: 2,
      high: 3,
      very_high: 4,
    };
    const severityIndex = {
      low: 0,
      medium: 1,
      high: 3,
      critical: 4,
    };
    const matrix = Array.from({ length: 5 }, () => Array.from({ length: 5 }, () => 0));
    (risks || []).forEach((risk) => {
      const row = probabilityIndex[risk.probability];
      const col = severityIndex[risk.severity];
      if (row === undefined || col === undefined) return;
      matrix[row][col] += 1;
    });
    return matrix;
  }

  function buildRiskMatrixCell(value, severity) {
    const cell = document.createElement("div");
    cell.className = "risk-matrix__cell";
    if (severity) {
      cell.dataset.severity = severity;
    }
    cell.textContent = value;
    return cell;
  }

  function createRiskMatrix(risks = null) {
    const container = document.createElement("div");
    container.className = "risk-matrix";
    container.dataset.component = "risk-matrix";
    const header = document.createElement("div");
    header.className = "risk-matrix__header";
    header.textContent = "Matriz de riesgo (5x5)";
    container.appendChild(header);

    const grid = document.createElement("div");
    grid.className = "risk-matrix__grid";
    const levels = ["Muy baja", "Baja", "Media", "Alta", "Muy alta"];
    const matrix = risks?.length ? buildRiskMatrixFromRisks(risks) : null;

    levels.forEach((label) => {
      const axis = document.createElement("div");
      axis.className = "risk-matrix__axis";
      axis.textContent = label;
      grid.appendChild(axis);
    });

    if (!matrix) {
      grid.appendChild(renderEmptyState("Sin riesgos registrados para este proyecto."));
      container.dataset.state = "empty";
    } else {
      container.dataset.state = "ready";
      matrix.forEach((row) => {
        row.forEach((value) => {
          let severity = "low";
          if (value >= 4) severity = "high";
          else if (value >= 2) severity = "medium";
          grid.appendChild(buildRiskMatrixCell(value, severity));
        });
      });
    }

    container.appendChild(grid);
    return container;
  }

  function statusToProgress(status) {
    if (status === "completed") return 100;
    if (status === "in_progress") return 50;
    if (status === "blocked") return 25;
    return 0;
  }

  function createGanttLite(tasks = null) {
    const container = document.createElement("div");
    container.className = "gantt-lite";
    container.dataset.component = "gantt-lite";
    const header = document.createElement("div");
    header.className = "gantt-lite__header";
    header.textContent = "Gantt (vista ligera)";
    container.appendChild(header);

    const list = document.createElement("div");
    list.className = "gantt-lite__list";
    const data =
      tasks && tasks.length
        ? tasks.map((task) => ({
            name: task.title || "Tarea",
            progress: statusToProgress(task.status),
          }))
        : null;

    if (!data) {
      list.appendChild(renderEmptyState("Sin tareas registradas para este proyecto."));
      container.dataset.state = "empty";
    } else {
      container.dataset.state = "ready";
      data.forEach((task) => {
        const row = document.createElement("div");
        row.className = "gantt-lite__row";
        const label = document.createElement("div");
        label.className = "gantt-lite__label";
        label.textContent = task.name;
        const bar = document.createElement("div");
        bar.className = "gantt-lite__bar";
        const fill = document.createElement("div");
        fill.className = "gantt-lite__fill";
        fill.style.width = `${Math.min(100, Math.max(0, task.progress))}%`;
        bar.appendChild(fill);
        row.appendChild(label);
        row.appendChild(bar);
        list.appendChild(row);
      });
    }

    container.appendChild(list);
    return container;
  }

  function createKanbanBoard(tasks = null) {
    const container = document.createElement("div");
    container.className = "kanban";
    container.dataset.component = "kanban";
    const header = document.createElement("div");
    header.className = "kanban__header";
    header.textContent = "Kanban (vista ligera)";
    container.appendChild(header);

    const board = document.createElement("div");
    board.className = "kanban__board";
    const columns = {
      pending: { title: "Pendiente", items: [] },
      in_progress: { title: "En progreso", items: [] },
      completed: { title: "Hecho", items: [] },
      blocked: { title: "Bloqueado", items: [] },
    };
    if (tasks && tasks.length) {
      tasks.forEach((task) => {
        const column = columns[task.status] || columns.pending;
        column.items.push(task.title || "Tarea");
      });
    }

    let hasItems = false;
    Object.values(columns).forEach((column) => {
      const col = document.createElement("div");
      col.className = "kanban__column";
      const title = document.createElement("div");
      title.className = "kanban__title";
      title.textContent = column.title;
      col.appendChild(title);
      if (!column.items.length) {
        col.appendChild(renderEmptyState("Sin items"));
      } else {
        hasItems = true;
        column.items.forEach((item) => {
          const card = document.createElement("div");
          card.className = "kanban__card";
          card.textContent = item;
          col.appendChild(card);
        });
      }
      board.appendChild(col);
    });

    container.dataset.state = hasItems ? "ready" : "empty";
    container.appendChild(board);
    return container;
  }

  async function fetchProjectSnapshot(projectId) {
    if (!projectId) return null;
    try {
      const response = await fetch(`/api/projects/proyectos/${projectId}/`);
      if (!response.ok) return null;
      return await response.json();
    } catch {
      return null;
    }
  }

  function renderAdvancedComponents(tasks, risks) {
    document.querySelectorAll("[data-component='risk-matrix']").forEach((el) => {
      el.innerHTML = "";
      el.appendChild(createRiskMatrix(risks));
      el.dataset.rendered = "true";
    });
    document.querySelectorAll("[data-component='gantt-lite']").forEach((el) => {
      el.innerHTML = "";
      el.appendChild(createGanttLite(tasks));
      el.dataset.rendered = "true";
    });
    document.querySelectorAll("[data-component='kanban']").forEach((el) => {
      el.innerHTML = "";
      el.appendChild(createKanbanBoard(tasks));
      el.dataset.rendered = "true";
    });
  }

  async function initAdvancedComponents(projectId) {
    const snapshot = await fetchProjectSnapshot(projectId);
    const tasks = snapshot?.tareas || [];
    const risks = snapshot?.riesgos || [];
    renderAdvancedComponents(tasks, risks);
  }

  function startAdvancedComponents(projectId, options = {}) {
    const refreshMs = options.refreshMs || 60000;
    initAdvancedComponents(projectId);
    if (!refreshMs) return null;
    const intervalId = setInterval(() => initAdvancedComponents(projectId), refreshMs);
    return () => clearInterval(intervalId);
  }

  window.SitecComponents = {
    labelFromName,
    createField,
    createSignaturePad,
    createEvidenceUploader,
    createGeoPicker,
    createRiskMatrix,
    createGanttLite,
    createKanbanBoard,
    initAdvancedComponents,
    startAdvancedComponents,
    contracts: COMPONENT_CONTRACTS,
  };
})();
