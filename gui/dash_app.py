"""
100% Python Real-Time Web Dashboard for Extractor Jurisprudencias TSJ Venezuela.
Built with Dash & Dash Bootstrap Components using DC3 Cyber Forensics Design System.
"""

import os
import json
import time
import webbrowser
import threading
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc

from src.utils import (
    SALAS_CHOICES, MESES_CHOICES, get_canonical_filenames, matches_sala, normalize_text
)
from src.buscador_tsj_excel import BuscadorTSJExcel
from src.database import TSJDatabaseManager
from src.scheduler import global_scheduler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Global Sync Progress Tracker for Multi-Sala Scraper
sync_progress = {
    "running": False,
    "percent": 0,
    "status": "Listo para iniciar escaneo multisala.",
    "sala": "",
    "finished": False
}


def worker_multisala_scraper():
    """
    Background worker thread that runs a live Playwright-based multi-Sala
    scraper against the TSJ Venezuela Liferay portal.
    
    Progress is tracked in the global sync_progress dict and polled by the
    Dash interval callback every 400ms for real-time UI updates.
    """
    global sync_progress
    sync_progress["running"] = True
    sync_progress["finished"] = False
    sync_progress["percent"] = 3
    sync_progress["status"] = "Iniciando Chromium headless — conectando con portal TSJ Venezuela..."

    salas_list = [
        ("constitucional",          "Sala Constitucional"),
        ("politico_administrativa",  "Sala Político-Administrativa"),
        ("casacion_civil",           "Sala de Casación Civil"),
        ("casacion_penal",           "Sala de Casación Penal"),
        ("casacion_social",          "Sala de Casación Social"),
        ("electoral",                "Sala Electoral"),
        ("plena",                    "Sala Plena"),
    ]

    buscador = BuscadorTSJExcel()
    total = len(salas_list)

    for idx, (s_key, s_nombre) in enumerate(salas_list, start=1):
        base_pct = int(((idx - 1) / total) * 90)

        sync_progress["sala"] = s_nombre
        sync_progress["percent"] = max(base_pct, 5)
        sync_progress["status"] = (
            f"[{idx}/{total}] 🌐 Playwright → {s_nombre}: "
            f"Cargando portal TSJ..."
        )

        # Real-time progress callback forwarded from Playwright scraper
        def _progress(pct: int, msg: str, _base=base_pct, _total=total):
            combined = _base + int(pct / _total)
            sync_progress["percent"] = min(combined, 90)
            sync_progress["status"] = f"[{idx}/{total}] {s_nombre}: {msg}"

        sala_choice = {"key": s_key, "nombre": s_nombre}
        try:
            buscador.actualizar_ultimas_jurisprudencias(
                sala_info=sala_choice,
                progress_callback=_progress,
            )
        except Exception as e:
            print(f"[Sync Worker] Error escaneando {s_nombre}: {e}")
            sync_progress["status"] = f"[{idx}/{total}] ⚠ {s_nombre}: Error — {str(e)[:80]}"

        time.sleep(0.2)

    sync_progress["percent"] = 100
    sync_progress["status"] = (
        "✅ Sincronización Multi-Sala 100% completada con Playwright. "
        "Bases de Datos SQLite y Matrices Excel actualizadas por Sala."
    )
    sync_progress["running"] = False
    sync_progress["finished"] = True



# Initialize Dash App with Bootstrap Theme and Root Assets Folder
app = dash.Dash(
    __name__,
    assets_folder=ASSETS_DIR,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css"
    ],
    title="Case Law Extractor powered by sha256.us"
)
app.config.suppress_callback_exceptions = True
server = app.server

# Custom Styles inline mapping to DC3 Cyber Center Design System
DC3_NAVY = "#061830"
DC3_GOLD = "#FFC809"
DC3_BLUE = "#0066CC"

# Define Options for Selects
sala_options = [{"label": f"🏛️ {v['nombre']}", "value": v["key"]} for v in SALAS_CHOICES.values()]
mes_options = [{"label": f"📅 {v['nombre']}", "value": v["key"]} for v in MESES_CHOICES.values()]

# Main Layout
app.layout = dbc.Container([
    
    # Store for caching current results & Local Cookies / Session Storage
    dcc.Store(id="store-decisiones"),
    dcc.Store(id="store-user-session", storage_type="local"),
    dcc.Store(id="store-cache", storage_type="session"),
    
    # 24-Hour Interval Auto-Sync Trigger (86400000 ms = 24 Hours)
    dcc.Interval(id="interval-24h-sync", interval=86400000, n_intervals=0),
    dcc.Interval(id="sync-progress-interval", interval=400, disabled=True),
    
    # Ultra-Minimalist Top Header / Menu Banner (50px Height)
    html.Header([
        dbc.Container([
            html.Div([
                # Left: Brand Identity
                html.Div([
                    html.Img(src="/assets/logo_sha256.svg", style={"height": "24px", "width": "24px"}, className="me-2"),
                    html.Span("Case Law Extractor", className="fw-bold text-white fs-6 me-1"),
                    html.Span("powered by sha256.us", className="text-warning fw-bold small me-3 d-none d-md-inline"),
                    html.Span("• TSJ Venezuela", className="text-light small opacity-50 d-none d-lg-inline")
                ], className="d-flex align-items-center"),
                
                # Right: Action Buttons
                html.Div([
                    dbc.Button([
                        html.I(className="fa-solid fa-arrows-rotate me-1"),
                        " Sincronizar (24h)"
                    ], id="btn-sync-24h", color="info", outline=True, size="sm", className="me-2 fw-bold text-white px-2 py-1"),
                    
                    dbc.Button([
                        html.I(className="fa-solid fa-file-excel me-1"),
                        " Generar Excel & SQLite"
                    ], id="btn-export", color="warning", size="sm", className="me-2 fw-bold text-dark px-2 py-1"),
                    
                    dbc.Button([
                        html.I(className="fa-solid fa-trash-can me-1"),
                        " Borrar Caché"
                    ], id="btn-clear-cache", color="danger", outline=True, size="sm", className="fw-bold px-2 py-1")
                ], className="d-flex align-items-center")
            ], className="d-flex justify-content-between align-items-center h-100")
        ], fluid=True, className="px-4 h-100")
    ], className="mb-3 border-bottom border-warning shadow-sm", style={"backgroundColor": DC3_NAVY, "height": "50px", "minHeight": "50px", "maxHeight": "50px", "overflow": "hidden"}),

    # Export Alert Container
    html.Div(id="export-alert-container", className="px-1"),

    # Filter Toolbar & Controls Card
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label([html.I(className="fa-solid fa-building-columns text-warning me-1"), " Sala o Juzgado TSJ:"], className="text-light fw-bold small mb-1"),
                    dbc.Select(id="select-sala", options=sala_options, value="todas", className="bg-dark text-light border-secondary")
                ], md=4),
                
                dbc.Col([
                    html.Label([html.I(className="fa-regular fa-calendar-days text-warning me-1"), " Período / Mes:"], className="text-light fw-bold small mb-1"),
                    dbc.Select(id="select-mes", options=mes_options, value="todo_el_ano", className="bg-dark text-light border-secondary")
                ], md=4),
                
                dbc.Col([
                    html.Label([html.I(className="fa-solid fa-magnifying-glass text-warning me-1"), " Buscar Término / Expediente:"], className="text-light fw-bold small mb-1"),
                    dbc.Input(id="input-search", placeholder="ej. Evidencia Digital, C25-664...", type="text", debounce=True, className="bg-dark text-light border-secondary")
                ], md=4),
            ], className="g-3"),
            
            # Animated Sync Progress Bar Container (DC3 Style)
            html.Div([
                dbc.Progress(
                    id="sync-progress-bar",
                    value=0,
                    label="0%",
                    striped=True,
                    animated=True,
                    color="warning",
                    className="mb-2 shadow-sm rounded-pill",
                    style={"height": "22px", "fontSize": "12px", "fontWeight": "bold"}
                ),
                html.Div("Iniciando escaneo multisala...", id="sync-progress-text", className="text-warning small text-center fw-bold")
            ], id="sync-progress-box", className="mt-3 p-3 rounded-3 border border-warning", style={"backgroundColor": "#071B33", "display": "none"})
        ], className="p-3")
    ], className="mb-4 shadow-sm border-0", style={"backgroundColor": "#0B2240", "borderLeft": f"4px solid {DC3_BLUE}"}),
    
    # Counter Bar
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H5([
                        html.I(className="fa-solid fa-list-check text-primary me-2"),
                        "Sentencias Encontradas: ",
                        dbc.Badge("0", id="badge-total", color="primary", className="ms-2")
                    ], className="fw-bold mb-0 text-dark")
                ], md=6),
                
                dbc.Col([
                    html.Small("Sincronizado en tiempo real con la base de datos local y WS TSJ", id="status-text", className="text-muted")
                ], md=6, className="text-end align-self-center")
            ])
        ], className="py-2")
    ], className="mb-4 border shadow-sm"),
    
    # Dynamic Cards Grid Container
    dbc.Row(id="cards-grid", className="g-4 mb-5"),
    
    # Modal Visor Pop-Up Extracto
    dbc.Modal([
        dbc.ModalHeader(
            dbc.ModalTitle([
                html.I(className="fa-solid fa-file-contract text-warning me-2"),
                "Ventana Emergente (Pop-Up) - Ver Extracto Oficial"
            ], className="fw-bold text-white"),
            close_button=True, className="bg-dark border-bottom border-warning"
        ),
        dbc.ModalBody([
            html.Div([
                dbc.Row([
                    dbc.Col([html.Strong("Sala: ", className="text-primary"), html.Span(id="popup-sala")], md=6),
                    dbc.Col([html.Strong("Expediente: ", className="text-primary"), html.Span(id="popup-expediente")], md=6),
                    dbc.Col([html.Strong("Sentencia N°: ", className="text-primary"), html.Span(id="popup-sentencia")], md=6),
                    dbc.Col([html.Strong("Fecha: ", className="text-primary"), html.Span(id="popup-fecha")], md=6),
                    dbc.Col([html.Strong("Magistrado Ponente: ", className="text-primary"), html.Span(id="popup-ponente")], md=12),
                    dbc.Col([html.Strong("Tema: ", className="text-primary"), html.Span(id="popup-tema")], md=12),
                    dbc.Col([html.Strong("Materia: ", className="text-primary"), html.Span(id="popup-materia")], md=12),
                ], className="g-2")
            ], className="p-3 mb-3 rounded border bg-light small"),
            
            html.H6([html.I(className="fa-solid fa-quote-left text-warning me-2"), "Extracto Oficial & Ratio Decidendi:"], className="fw-bold text-dark mb-2"),
            html.Div(id="popup-extracto-text", className="p-3 bg-white rounded border shadow-sm text-dark lead fs-6 mb-3", style={"maxHeight": "250px", "overflowY": "auto"}),
            
            html.Label("URL Enlace Directo que abrió este Pop-Up:", className="fw-bold small text-muted"),
            dbc.InputGroup([
                dbc.Input(id="popup-url-input", readonly=True, className="font-monospace small bg-light"),
                dbc.Button([html.I(className="fa-solid fa-up-right-from-square me-1"), "Abrir TSJ"], id="popup-link-btn", href="#", target="_blank", color="primary")
            ])
        ], className="p-4"),
        dbc.ModalFooter([
            dbc.Button("Cerrar", id="btn-close-modal", className="ms-auto", color="secondary")
        ], className="bg-light")
    ], id="modal-popup", size="lg", centered=True, is_open=False),
    
    # Ultra-Minimalist Dashboard Footer (50px Height)
    html.Footer([
        dbc.Container([
            html.Div([
                html.Div([
                    html.Img(src="/assets/logo_sha256.svg", style={"height": "22px", "width": "22px"}, className="me-2"),
                    html.Span("Case Law Extractor", className="fw-bold text-white small me-1"),
                    html.Span("powered by sha256.us", className="text-warning fw-bold small me-3"),
                    html.Span("• TSJ Venezuela 2019-2026", className="text-light small opacity-50 d-none d-md-inline")
                ], className="d-flex align-items-center"),
                html.Div([
                    html.Span("Dashboard 100% Python", className="badge bg-dark text-warning border border-warning me-3 small px-2 py-1"),
                    html.A([
                        html.I(className="fa-brands fa-github me-1"),
                        "GitHub"
                    ], href="https://github.com/julljoll/case-law-extractor", target="_blank", className="text-warning text-decoration-none small me-3 fw-bold"),
                    html.A("sha256.us", href="https://sha256.us", target="_blank", className="text-light text-decoration-none small opacity-75")
                ], className="d-flex align-items-center")
            ], className="d-flex justify-content-between align-items-center h-100")
        ], fluid=True, className="px-4 h-100")
    ], className="mt-auto border-top border-warning shadow-sm", style={"backgroundColor": "#061830", "height": "50px", "minHeight": "50px", "maxHeight": "50px", "overflow": "hidden"})

], fluid=True, className="px-4 py-3 min-vh-100 d-flex flex-column", style={"backgroundColor": "#F8FAFC"})


# --- CALLBACKS REACTIVOS ---

@app.callback(
    [Output("cards-grid", "children"),
     Output("badge-total", "children"),
     Output("status-text", "children"),
     Output("store-decisiones", "data")],
    [Input("select-sala", "value"),
     Input("select-mes", "value"),
     Input("input-search", "value"),
     Input("interval-24h-sync", "n_intervals")]
)
def update_dashboard(sala_key, mes_key, search_query, n_interval):
    """Fetches real-time decisions and updates the grid reactively."""
    buscador = BuscadorTSJExcel()

    # Resolve labels & canonical SQLite DB
    sala_choice = next((v for v in SALAS_CHOICES.values() if v["key"] == sala_key), SALAS_CHOICES["0"])
    mes_choice = next((v for v in MESES_CHOICES.values() if v["key"] == mes_key), MESES_CHOICES["0"])

    db_path, filepath, clean_name = get_canonical_filenames(sala_choice["key"])
    db_mgr = TSJDatabaseManager(db_path=db_path)
    records = db_mgr.obtener_todas()

    if not records:
        # Fallback to general database or seed dataset if empty
        db_mgr_gen = TSJDatabaseManager(db_path="data/Databases_SQLite/tsj_todas_las_salas.db")
        records = db_mgr_gen.obtener_todas()
        if not records:
            records = buscador.get_real_tsj_database()

    # Resilient Sala filtering using matches_sala (fixes Sala Penal accent issue)
    if sala_choice["key"] != "todas":
        records = [r for r in records if matches_sala(r.get("sala", ""), sala_choice["key"])]

    # Resilient Month filtering
    if mes_choice["key"] != "todo_el_ano":
        target_mes = normalize_text(mes_choice["nombre"])
        records = [r for r in records if target_mes in normalize_text(r.get("fecha", ""))]

    # Keyword search filtering
    if search_query and search_query.strip():
        q = normalize_text(search_query)
        records = [
            r for r in records
            if q in normalize_text(r.get("tema", ""))
            or q in normalize_text(r.get("materia", ""))
            or q in normalize_text(r.get("asunto", ""))
            or q in normalize_text(r.get("extracto", ""))
            or q in normalize_text(r.get("expediente", ""))
            or q in normalize_text(r.get("numero_sentencia", ""))
        ]

    # Build Card Components Grid
    grid_children = []
    if not records:
        grid_children.append(
            dbc.Col(
                html.Div([
                    html.I(className="fa-solid fa-folder-open text-muted display-4 mb-3 d-block"),
                    html.H5("No se encontraron sentencias con los filtros aplicados", className="fw-bold text-dark"),
                    html.P("Intente cambiar la Sala seleccionada o limpiar el término de búsqueda.", className="text-muted small")
                ], className="p-5 bg-white rounded-3 border shadow-sm text-center col-12")
            )
        )
    else:
        for idx, dec in enumerate(records):
            extracto_short = (dec.get("extracto") or dec.get("asunto") or "")[:130] + "..."
            
            card = dbc.Col(
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            dbc.Badge([html.I(className="fa-solid fa-building-columns me-1"), dec.get("sala")], color="primary", className="px-2 py-1 me-2"),
                            dbc.Badge([html.I(className="fa-regular fa-calendar me-1"), str(dec.get("fecha") or dec.get("ano"))], color="warning", className="text-dark px-2 py-1")
                        ], className="d-flex justify-content-between mb-3"),
                        
                        html.H5(f"Sentencia N° {dec.get('numero_sentencia')}", className="fw-bold text-dark mb-1"),
                        html.H6(["Expediente: ", dbc.Badge(dec.get("expediente"), color="secondary", className="font-monospace")], className="text-muted small mb-3"),
                        
                        html.P([html.Strong("Ponente: "), dec.get("ponente", "No especificado")], className="small text-dark mb-1"),
                        html.P([html.Strong("Tema: "), dec.get("tema", "Jurisprudencia")], className="small text-dark mb-1"),
                        html.P([html.Strong("Materia: "), dec.get("materia", "Derecho Procesal")], className="small text-dark mb-3"),
                        
                        html.Div([
                            html.Strong([html.I(className="fa-solid fa-up-right-from-square me-1"), " Ver Extracto Pop-Up:"], className="d-block mb-1 text-primary small"),
                            html.Span(extracto_short, className="small text-secondary")
                        ], className="p-2 bg-light rounded border-start border-3 border-warning mb-3"),
                        
                        html.Div([
                            dbc.Button([html.I(className="fa-solid fa-eye me-1"), "Ver Extracto Pop-Up Completo"], id={"type": "btn-open-modal", "index": idx}, color="outline-primary", size="sm", className="w-100 fw-bold mb-2"),
                            dbc.Button([html.I(className="fa-solid fa-link me-1"), " Link Directo TSJ"], href=dec.get("link_directo") or dec.get("url"), target="_blank", color="dark", size="sm", className="w-100 font-monospace text-truncate")
                        ], className="pt-2 border-top")
                    ], className="p-4 d-flex flex-column justify-content-between h-100")
                ], className="h-100 shadow-sm border-light rounded-3")
            , md=6, lg=4)
            grid_children.append(card)

    status_msg = f"Filtros Activos: {sala_choice['nombre']} | Período: {mes_choice['nombre']}"
    return grid_children, str(len(records)), status_msg, records


@app.callback(
    [Output("modal-popup", "is_open"),
     Output("popup-sala", "children"),
     Output("popup-expediente", "children"),
     Output("popup-sentencia", "children"),
     Output("popup-fecha", "children"),
     Output("popup-ponente", "children"),
     Output("popup-tema", "children"),
     Output("popup-materia", "children"),
     Output("popup-extracto-text", "children"),
     Output("popup-url-input", "value"),
     Output("popup-link-btn", "href")],
    [Input({"type": "btn-open-modal", "index": dash.ALL}, "n_clicks"),
     Input("btn-close-modal", "n_clicks")],
    [State("store-decisiones", "data"),
     State("modal-popup", "is_open")]
)
def toggle_modal(open_clicks, close_click, data, is_open):
    """Opens/Closes Pop-Up modal with decision details."""
    ctx = callback_context
    if not ctx.triggered:
        return False, "", "", "", "", "", "", "", "", "", "#"

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "btn-close-modal":
        return False, "", "", "", "", "", "", "", "", "", "#"

    try:
        id_dict = json.loads(button_id)
        idx = id_dict["index"]
        dec = data[idx]
        url = dec.get("link_directo") or dec.get("url") or "#"
        return (
            True,
            dec.get("sala", ""),
            dec.get("expediente", ""),
            dec.get("numero_sentencia", ""),
            str(dec.get("fecha") or dec.get("ano") or ""),
            dec.get("ponente", "No especificado"),
            dec.get("tema", "General"),
            dec.get("materia", "General"),
            dec.get("extracto") or dec.get("asunto") or "",
            url,
            url
        )
    except Exception:
        return False, "", "", "", "", "", "", "", "", "", "#"


@app.callback(
    Output("export-alert-container", "children"),
    Input("btn-export", "n_clicks"),
    [State("select-sala", "value"),
     State("select-mes", "value"),
     State("input-search", "value")],
    prevent_initial_call=True
)
def trigger_export(n_clicks, sala_key, mes_key, kw):
    """Triggers dynamic SQLite DB and Excel pairing in 100% Python."""
    if not n_clicks:
        return dash.no_update

    sala_choice = next((v for v in SALAS_CHOICES.values() if v["key"] == sala_key), SALAS_CHOICES["0"])
    mes_choice = next((v for v in MESES_CHOICES.values() if v["key"] == mes_key), MESES_CHOICES["0"])

    buscador = BuscadorTSJExcel()
    excel_path = buscador.actualizar_ultimas_jurisprudencias(
        palabra_clave=kw or "",
        ano_inicio=2019,
        ano_fin=2026,
        sala_info=sala_choice,
        mes_info=mes_choice
    )

    return dbc.Alert([
        html.I(className="fa-solid fa-circle-check me-2"),
        f"Matriz Excel y BD SQLite generadas con éxito en: {os.path.basename(excel_path)}"
    ], color="success", dismissable=True, className="mt-2 py-2 small")


@app.callback(
    [Output("select-sala", "value"),
     Output("select-mes", "value"),
     Output("input-search", "value"),
     Output("export-alert-container", "children", allow_duplicate=True)],
    Input("btn-clear-cache", "n_clicks"),
    prevent_initial_call=True
)
def clear_cache_and_cookies(n_clicks):
    """Clears search cache, cookies/local storage, and resets UI inputs."""
    if not n_clicks:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
        
    deleted_files = TSJDatabaseManager.vaciar_cache_busquedas()
    
    alert = dbc.Alert([
        html.I(className="fa-solid fa-trash-can me-2"),
        f"Caché de datos, cookies y {deleted_files} archivo(s) de búsqueda vaciados con éxito."
    ], color="danger", dismissable=True, className="mt-2 py-2 small fw-bold")
    
    return "todas", "todo_el_ano", "", alert


@app.callback(
    Output("export-alert-container", "children", allow_duplicate=True),
    [Input("btn-sync-24h", "n_clicks"),
     Input("interval-24h-sync", "n_intervals")],
    prevent_initial_call=True
)
def trigger_24h_sync(n_clicks, n_intervals):
    """Triggers or checks background 24-hour auto-updater sync."""
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update
        
    res = global_scheduler.force_update()
    if res.get("status") == "success":
        msg = f"Sincronización 24h completada con éxito. Base de Datos actualizada ({res.get('total_registros', 0)} sentencias)."
        color = "info"
    else:
        msg = f"Sincronización 24h realizada: {res.get('message', 'Base de datos en sintonía con el TSJ.')}"
        color = "warning"

    return dbc.Alert([
        html.I(className="fa-solid fa-arrows-rotate me-2"),
        msg
    ], color=color, dismissable=True, className="mt-2 py-2 small fw-bold")



@app.callback(
    [Output("sync-progress-interval", "disabled"),
     Output("sync-progress-box", "style")],
    Input("btn-sync-24h", "n_clicks"),
    prevent_initial_call=True
)
def start_sync_process(n_clicks):
    """Launches multi-sala scraper background thread and displays animated progress bar."""
    if not n_clicks:
        return True, {"display": "none"}
    
    if not sync_progress["running"]:
        t = threading.Thread(target=worker_multisala_scraper)
        t.daemon = True
        t.start()
        
    return False, {"display": "block"}


@app.callback(
    [Output("sync-progress-bar", "value"),
     Output("sync-progress-bar", "label"),
     Output("sync-progress-bar", "color"),
     Output("sync-progress-text", "children"),
     Output("sync-progress-interval", "disabled", allow_duplicate=True),
     Output("select-sala", "value", allow_duplicate=True)],
    Input("sync-progress-interval", "n_intervals"),
    State("select-sala", "value"),
    prevent_initial_call=True
)
def update_sync_progress_bar(n_intervals, current_sala):
    """Polls background worker thread progress and updates UI progress bar reactively."""
    pct = sync_progress["percent"]
    status = sync_progress["status"]
    color = "success" if pct == 100 else "warning"
    label = f"{pct}%"
    
    disable_interval = False
    new_sala_val = dash.no_update
    
    if sync_progress["finished"] and not sync_progress["running"]:
        disable_interval = True
        # Force re-render of current active sala view with newly fetched decisions
        new_sala_val = current_sala
        
    return pct, label, color, status, disable_interval, new_sala_val


def run_dash_app(port=8050, debug=False, open_browser=True):
    """Runs the 100% Python Dash Dashboard App and automatically opens browser."""
    url = f"http://127.0.0.1:{port}/"
    print(f"\n===============================================================================")
    print(f"  [ TSJ CYBER FORENSICS LAB ] case-law-extractor powered by sha256.us")
    print(f"  Servidor Dash Web Activo en: {url}")
    print(f"===============================================================================\n")
    
    if open_browser:
        threading.Timer(1.2, lambda: webbrowser.open_new(url)).start()

    if hasattr(app, "run"):
        app.run(host="127.0.0.1", port=port, debug=debug)
    else:
        app.run_server(host="127.0.0.1", port=port, debug=debug)


if __name__ == "__main__":
    run_dash_app()
