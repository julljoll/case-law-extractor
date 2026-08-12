"""
100% Python Real-Time Web Dashboard for Extractor Jurisprudencias TSJ Venezuela.
Built with Dash & Dash Bootstrap Components using DC3 Cyber Forensics Design System.
"""

import os
import json
import webbrowser
import threading
import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc

from src.utils import SALAS_CHOICES, MESES_CHOICES
from src.buscador_tsj_excel import BuscadorTSJExcel
from src.database import TSJDatabaseManager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Initialize Dash App with Bootstrap Theme and Root Assets Folder
app = dash.Dash(
    __name__,
    assets_folder=ASSETS_DIR,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css"
    ],
    title="case-law-extractor powered by sha256.us - Dashboard Web Python"
)
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
    
    # Store for caching current results
    dcc.Store(id="store-decisiones"),
    
    # Header Banner (DC3 Style Printable Header with SHA256 Logo)
    dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Img(src="/assets/logo_sha256.svg", style={"height": "65px", "width": "65px"}, className="me-3"),
                        html.Div([
                            html.Span([
                                html.I(className="fa-solid fa-shield-halved me-2"),
                                "CASE-LAW-EXTRACTOR • POWERED BY SHA256.US"
                            ], className="badge bg-warning text-dark mb-2 px-3 py-2 fw-bold rounded-pill"),
                            html.H2("case-law-extractor powered by sha256.us", className="text-white fw-bold mb-1"),
                            html.P("Buscador y Dashboard en Tiempo Real TSJ Venezuela (2019 - 2026). Generación emparejada de Bases de Datos SQLite (.db) y matrices Excel (.xlsx) en 100% Python.", className="text-light mb-0 small opacity-75")
                        ])
                    ], className="d-flex align-items-center")
                ], md=8),
                
                dbc.Col([
                    dbc.Button([
                        html.I(className="fa-solid fa-file-excel me-2"),
                        "Generar Excel & SQLite"
                    ], id="btn-export", color="warning", className="fw-bold w-100 mb-2 py-2 text-dark"),
                    
                    html.Div(id="export-alert-container")
                ], md=4, className="text-end align-self-center")
            ]),
            
            # Control Controls
            html.Div([
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
                        dbc.Input(id="input-search", placeholder="ej. Evidencia Digital, C25-664...", type="text", className="bg-dark text-light border-secondary")
                    ], md=4),
                ], className="g-3 mt-1")
            ], className="p-3 mt-3 rounded-3", style={"backgroundColor": "#0B2240", "border": f"1.5px solid {DC3_BLUE}"})
        ])
    ], className="mb-4 shadow-lg border-0", style={"backgroundColor": DC3_NAVY, "borderBottom": f"4px solid {DC3_GOLD}"}),
    
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
    
    # Footer
    html.Footer([
        html.P("case-law-extractor powered by sha256.us • DC3 Cyber Forensics Style (100% Python)", className="mb-1 fw-bold text-warning"),
        html.P("Estándar Folio Vertical Imprimible • Base de Datos SQLite (.db) y Matriz Excel (.xlsx) Sincronizadas 1:1", className="small text-muted mb-0")
    ], className="bg-dark text-light py-4 border-top border-warning text-center mt-auto")

], fluid=True, className="px-4 py-3 min-vh-100 d-flex flex-column", style={"backgroundColor": "#F8FAFC"})


# --- CALLBACKS REACTIVOS ---

@app.callback(
    [Output("cards-grid", "children"),
     Output("badge-total", "children"),
     Output("status-text", "children"),
     Output("store-decisiones", "data")],
    [Input("select-sala", "value"),
     Input("select-mes", "value"),
     Input("input-search", "value")]
)
def update_dashboard(sala_key, mes_key, search_query):
    """Fetches real-time decisions and updates the grid reactively."""
    buscador = BuscadorTSJExcel()
    records = buscador.get_real_tsj_database()

    # Resolve labels
    sala_choice = next((v for v in SALAS_CHOICES.values() if v["key"] == sala_key), SALAS_CHOICES["0"])
    mes_choice = next((v for v in MESES_CHOICES.values() if v["key"] == mes_key), MESES_CHOICES["0"])

    # Filter by Sala
    if sala_choice["key"] != "todas":
        target_sala = sala_choice["nombre"].lower()
        records = [r for r in records if target_sala in r.get("sala", "").lower()]

    # Filter by Month
    if mes_choice["key"] != "todo_el_ano":
        target_mes = mes_choice["nombre"].lower()
        records = [r for r in records if target_mes in r.get("fecha", "").lower()]

    # Filter by search keyword
    if search_query and search_query.strip():
        q = search_query.lower()
        records = [
            r for r in records
            if q in r.get("tema", "").lower()
            or q in r.get("materia", "").lower()
            or q in r.get("asunto", "").lower()
            or q in r.get("extracto", "").lower()
            or q in r.get("expediente", "").lower()
            or q in r.get("numero_sentencia", "").lower()
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
