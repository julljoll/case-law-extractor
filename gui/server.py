"""
DC3 Cyber Forensics Laboratory - TSJ Real-Time Web Dashboard Proxy Server.
Connects the web frontend (gui/index.html) with TSJ Liferay API services and local DB generators.
"""

import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Dict, List, Any

from src.utils import SALAS_CHOICES, MESES_CHOICES, load_config, sanitize_search_name
from src.extractor import JurisprudenciaExtractor
from src.database import TSJDatabaseManager
from src.buscador_tsj_excel import BuscadorTSJExcel

PORT = 8080
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TSJDashboardHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler bridging GUI requests to TSJ API & SQLite/Excel generators."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def _set_headers(self, content_type="application/json", status=200):
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(status=204)

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)

        # Route API endpoints
        if parsed_path.path == "/api/salas":
            self._set_headers()
            salas_list = list(SALAS_CHOICES.values())
            self.wfile.write(json.dumps({"status": "ok", "salas": salas_list}, ensure_ascii=False).encode("utf-8"))
            return

        elif parsed_path.path == "/api/meses":
            self._set_headers()
            meses_list = list(MESES_CHOICES.values())
            self.wfile.write(json.dumps({"status": "ok", "meses": meses_list}, ensure_ascii=False).encode("utf-8"))
            return

        elif parsed_path.path == "/api/decisiones":
            self._set_headers()
            sala_key = query_params.get("sala", ["todas"])[0]
            mes_key = query_params.get("mes", ["todo_el_ano"])[0]
            search_query = query_params.get("q", [""])[0]

            # Resolve choices
            sala_choice = next((v for v in SALAS_CHOICES.values() if v["key"] == sala_key or v["code"] == sala_key), SALAS_CHOICES["0"])
            mes_choice = next((v for v in MESES_CHOICES.values() if v["key"] == mes_key or v["code"] == mes_key), MESES_CHOICES["0"])

            buscador = BuscadorTSJExcel()
            records = buscador.get_real_tsj_database()

            # Filter by Sala
            if sala_choice["key"] != "todas":
                target_sala = sala_choice["nombre"].lower()
                records = [r for r in records if target_sala in r.get("sala", "").lower()]

            # Filter by Month
            if mes_choice["key"] != "todo_el_ano":
                target_mes = mes_choice["nombre"].lower()
                records = [r for r in records if target_mes in r.get("fecha", "").lower()]

            # Filter by keyword
            if search_query.strip():
                q_lower = search_query.lower()
                records = [
                    r for r in records
                    if q_lower in r.get("tema", "").lower()
                    or q_lower in r.get("materia", "").lower()
                    or q_lower in r.get("asunto", "").lower()
                    or q_lower in r.get("extracto", "").lower()
                    or q_lower in r.get("expediente", "").lower()
                    or q_lower in r.get("numero_sentencia", "").lower()
                ]

            response_data = {
                "status": "ok",
                "sala": sala_choice,
                "mes": mes_choice,
                "total": len(records),
                "decisiones": records
            }
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))
            return

        elif parsed_path.path == "/api/stats":
            self._set_headers()
            all_dbs = TSJDatabaseManager.listar_todas_las_bases_de_datos()
            self.wfile.write(json.dumps({"status": "ok", "databases": all_dbs}, ensure_ascii=False).encode("utf-8"))
            return

        elif parsed_path.path == "/gui" or parsed_path.path == "/gui/":
            self.path = "/gui/index.html"
            return super().do_GET()

        # Serve static files normally
        return super().do_GET()

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        
        try:
            body = json.loads(post_data)
        except Exception:
            body = {}

        if parsed_path.path == "/api/export/excel":
            self._set_headers()
            sala_key = body.get("sala", "todas")
            mes_key = body.get("mes", "todo_el_ano")
            kw = body.get("palabra_clave", "")

            sala_choice = next((v for v in SALAS_CHOICES.values() if v["key"] == sala_key), SALAS_CHOICES["0"])
            mes_choice = next((v for v in MESES_CHOICES.values() if v["key"] == mes_key), MESES_CHOICES["0"])

            buscador = BuscadorTSJExcel()
            excel_path = buscador.actualizar_ultimas_jurisprudencias(
                palabra_clave=kw,
                ano_inicio=2019,
                ano_fin=2026,
                sala_info=sala_choice,
                mes_info=mes_choice
            )

            rel_path = os.path.relpath(excel_path, BASE_DIR).replace("\\", "/")
            self.wfile.write(json.dumps({
                "status": "ok",
                "message": "Matriz Excel y Base de Datos SQLite generadas exitosamente",
                "excel_path": excel_path,
                "url": f"/{rel_path}"
            }, ensure_ascii=False).encode("utf-8"))
            return

        self._set_headers(status=404)
        self.wfile.write(json.dumps({"status": "error", "message": "Endpoint no encontrado"}).encode("utf-8"))


def start_server(port: int = PORT):
    """Launches the real-time TSJ Dashboard HTTP Server."""
    print(f"\n===============================================================================")
    print(f"  [ TSJ CYBER FORENSICS LAB ] INICIANDO DASHBOARD WEB EN TIEMPO REAL")
    print(f"  Servidor HTTP activo en: http://localhost:{port}/gui/index.html")
    print(f"===============================================================================\n")
    server_address = ("", port)
    httpd = HTTPServer(server_address, TSJDashboardHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor finalizado por el usuario.")
        httpd.server_close()


if __name__ == "__main__":
    start_server()
