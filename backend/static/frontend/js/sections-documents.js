/**
 * sections-documents.js
 * Lista documentos usando /api/documents/ (si existe) o muestra placeholder.
 */

document.addEventListener("DOMContentLoaded", () => {
  const status = document.getElementById("documentsStatus");
  const table = document.getElementById("documentsTable");

  const setStatus = (text, level = "info") => {
    if (!status) return;
    status.textContent = text;
    status.setAttribute("data-level", level);
  };

  const renderTable = (rows) => {
    if (!table) return;
    table.innerHTML = "";
    const columns = [
      { label: "Nombre", value: (r) => r.name || r.title || "--" },
      { label: "Tipo", value: (r) => r.type || "--" },
      { label: "Creado", value: (r) => r.created_at || "--" },
    ];
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
          td.textContent = c.value(r) ?? "--";
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
      // Usar dataLoader si está disponible
      const url = "/api/documents/";
      let data;
      
      if (window.dataLoader) {
        try {
          data = await window.dataLoader.fetchWithCache(url, { cache: true, ttl: 60000 });
        } catch (e) {
          // Si falla, puede ser que el endpoint no exista
          setStatus("Sin acceso o módulo no disponible", "warn");
          if (window.loadingStates && table) {
            window.loadingStates.hideLoading(table);
          }
          renderTable([]);
          return;
        }
      } else {
        const res = await fetch(url, { credentials: "include" });
        if (!res.ok) {
          setStatus("Sin acceso o módulo no disponible", "warn");
          if (window.loadingStates && table) {
            window.loadingStates.hideLoading(table);
          }
          renderTable([]);
          return;
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
      console.error("[Documents] Error:", e);
      
      // Mostrar error con loadingStates si está disponible
      if (window.loadingStates && table) {
        window.loadingStates.showError(
          table,
          "Error al cargar documentos",
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

