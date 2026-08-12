/* ==========================================================================
   DC3 Cyber Forensics Laboratory - TSJ Dashboard Client Script
   Handles real-time API queries, dynamic rendering, and Pop-Up modals.
   ========================================================================== */

let decisionesCache = [];
let extractoModal = null;

document.addEventListener("DOMContentLoaded", function () {
  extractoModal = new bootstrap.Modal(document.getElementById("modalExtracto"));
  cargarDecisiones();
});

function cargarDecisiones() {
  const sala = document.getElementById("selectSala").value;
  const mes = document.getElementById("selectMes").value;
  const search = document.getElementById("inputSearch").value;
  const statusMsg = document.getElementById("statusMessage");

  statusMsg.innerHTML = '<i class="fa-solid fa-spinner fa-spin text-warning me-1"></i> Consultando servidor TSJ en tiempo real...';

  const url = `/api/decisiones?sala=${encodeURIComponent(sala)}&mes=${encodeURIComponent(mes)}&q=${encodeURIComponent(search)}`;

  fetch(url)
    .then(res => res.json())
    .then(data => {
      if (data.status === "ok") {
        decisionesCache = data.decisiones;
        renderizarTarjetas(data.decisiones);
        document.getElementById("counterTotal").innerText = data.total;
        statusMsg.innerHTML = `Sincronizado: <b>${data.sala.nombre}</b> | <b>${data.mes.nombre}</b>`;
      } else {
        statusMsg.innerHTML = '<span class="text-danger">Error al consultar datos</span>';
      }
    })
    .catch(err => {
      console.error("Error al conectar con el servidor proxy:", err);
      statusMsg.innerHTML = '<span class="text-danger">No se pudo conectar con el backend local. Inicie gui/server.py</span>';
    });
}

function renderizarTarjetas(lista) {
  const container = document.getElementById("cardsContainer");
  container.innerHTML = "";

  if (lista.length === 0) {
    container.innerHTML = `
      <div class="col-12 text-center py-5">
        <div class="p-5 bg-white rounded-3 border shadow-sm">
          <i class="fa-solid fa-folder-open text-muted display-4 mb-3 d-block"></i>
          <h5 class="fw-bold text-dark">No se encontraron sentencias con los filtros aplicados</h5>
          <p class="text-muted small">Intente cambiar la Sala seleccionada o limpiar el término de búsqueda.</p>
        </div>
      </div>`;
    return;
  }

  lista.forEach((dec, index) => {
    const col = document.createElement("div");
    col.className = "col-md-6 col-lg-4";

    col.innerHTML = `
      <div class="dc3-card-item p-4 h-100 d-flex flex-column justify-content-between">
        <div>
          <div class="d-flex justify-content-between align-items-center mb-3">
            <span class="dc3-badge-sala"><i class="fa-solid fa-building-columns me-1"></i> ${dec.sala}</span>
            <span class="dc3-badge-fecha"><i class="fa-regular fa-calendar me-1"></i> ${dec.fecha || dec.ano}</span>
          </div>

          <h5 class="fw-bold text-dark mb-1">Sentencia N° ${dec.numero_sentencia}</h5>
          <h6 class="text-muted small mb-3">Expediente: <span class="badge bg-secondary font-monospace">${dec.expediente}</span></h6>

          <p class="small text-dark mb-2"><strong>Ponente:</strong> ${dec.ponente || "No especificado"}</p>
          <p class="small text-dark mb-2"><strong>Tema:</strong> ${dec.tema || "Jurisprudencia"}</p>
          <p class="small text-dark mb-3"><strong>Materia:</strong> ${dec.materia || "Derecho Procesal"}</p>

          <div class="dc3-popup-preview mb-3">
            <strong class="d-block mb-1 text-primary"><i class="fa-solid fa-up-right-from-square me-1"></i> Ver Extracto Pop-Up:</strong>
            ${truncateText(dec.extracto || dec.asunto, 130)}
          </div>
        </div>

        <div class="d-grid gap-2 pt-2 border-top">
          <button class="btn btn-outline-primary btn-sm fw-bold" onclick="abrirModalExtracto(${index})">
            <i class="fa-solid fa-eye me-1"></i> Ver Extracto Pop-Up Completo
          </button>
          <a href="${dec.link_directo || dec.url}" target="_blank" class="btn btn-dark btn-sm font-monospace text-truncate">
            <i class="fa-solid fa-link me-1"></i> ${dec.link_directo || dec.url}
          </a>
        </div>
      </div>`;

    container.appendChild(col);
  });
}

function abrirModalExtracto(index) {
  const dec = decisionesCache[index];
  if (!dec) return;

  document.getElementById("popupSala").innerText = dec.sala;
  document.getElementById("popupExpediente").innerText = dec.expediente;
  document.getElementById("popupSentencia").innerText = dec.numero_sentencia;
  document.getElementById("popupFecha").innerText = dec.fecha || dec.ano;
  document.getElementById("popupPonente").innerText = dec.ponente || "No especificado";
  document.getElementById("popupTema").innerText = dec.tema || "General";
  document.getElementById("popupMateria").innerText = dec.materia || "General";
  document.getElementById("popupTextoExtracto").innerText = dec.extracto || dec.asunto || dec.texto_completo;

  const url = dec.link_directo || dec.url;
  document.getElementById("popupLinkUrl").value = url;
  document.getElementById("popupBtnAbrir").href = url;

  extractoModal.show();
}

function copiarLinkUrl() {
  const input = document.getElementById("popupLinkUrl");
  input.select();
  navigator.clipboard.writeText(input.value);
  alert("¡Link Directo copiado al portapapeles!\n" + input.value);
}

function filtrarInstantaneo() {
  const q = document.getElementById("inputSearch").value.toLowerCase();
  const filtradas = decisionesCache.filter(r =>
    (r.tema && r.tema.toLowerCase().includes(q)) ||
    (r.materia && r.materia.toLowerCase().includes(q)) ||
    (r.asunto && r.asunto.toLowerCase().includes(q)) ||
    (r.extracto && r.extracto.toLowerCase().includes(q)) ||
    (r.expediente && r.expediente.toLowerCase().includes(q)) ||
    (r.numero_sentencia && r.numero_sentencia.toLowerCase().includes(q))
  );
  renderizarTarjetas(filtradas);
  document.getElementById("counterTotal").innerText = filtradas.length;
}

function exportarExcelDB() {
  const sala = document.getElementById("selectSala").value;
  const mes = document.getElementById("selectMes").value;
  const kw = document.getElementById("inputSearch").value;
  const btn = document.getElementById("btnExportExcel");

  btn.disabled = true;
  btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i> Exportando...';

  fetch("/api/export/excel", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sala: sala, mes: mes, palabra_clave: kw })
  })
    .then(res => res.json())
    .then(data => {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-file-excel me-2"></i> Generar Excel & SQLite';
      if (data.status === "ok") {
        alert("¡ÉXITO!\n\n" + data.message + "\n\nRuta archivo: " + data.excel_path);
        window.open(data.url, "_blank");
      } else {
        alert("Error al exportar: " + data.message);
      }
    })
    .catch(err => {
      btn.disabled = false;
      btn.innerHTML = '<i class="fa-solid fa-file-excel me-2"></i> Generar Excel & SQLite';
      alert("Error al conectar con el servidor proxy de exportación.");
    });
}

function verBasesDatosSQLite() {
  fetch("/api/stats")
    .then(res => res.json())
    .then(data => {
      if (data.status === "ok") {
        let msg = "BASES DE DATOS SQLITE ENCONTRADAS:\n\n";
        data.databases.forEach(db => {
          msg += `• ${db.filename}: ${db.total_registros} registros\n`;
        });
        alert(msg);
      }
    });
}

function truncateText(str, maxLen) {
  if (!str) return "";
  if (str.length <= maxLen) return str;
  return str.substring(0, maxLen) + "...";
}
