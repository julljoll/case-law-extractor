"""
SQLite Database Manager for TSJ Venezuela Jurisprudence.
Provides local relational storage and fast queries for scanned jurisprudence records,
including Chamber, Expediente, Sentencia, Date, Topic, Subject, Extract Pop-up detail, and Direct URL links.
"""

import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple


class TSJDatabaseManager:
    """Manages local SQLite databases for TSJ Venezuela Jurisprudence searches."""

    def __init__(self, db_path: str = "data/Databases_SQLite/Escaneo_Global_TSJ_2019_2026.db"):
        self.db_path = db_path
        folder = os.path.dirname(self.db_path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Returns SQLite database connection with dictionary row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Initializes SQLite tables and indexes."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisiones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sala TEXT NOT NULL,
                numero_sentencia TEXT,
                expediente TEXT,
                fecha TEXT,
                ano INTEGER,
                tema TEXT,
                materia TEXT,
                asunto TEXT,
                extracto TEXT,
                link_directo TEXT UNIQUE,
                fecha_escaneo TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_link_directo ON decisiones(link_directo)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_sala ON decisiones(sala)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_expediente ON decisiones(expediente)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ano ON decisiones(ano)')
            conn.commit()

    def insertar_o_actualizar(self, decision: Dict[str, Any]) -> bool:
        """Inserts or updates a decision record in SQLite database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                INSERT INTO decisiones (
                    sala, numero_sentencia, expediente, fecha, ano, tema, materia, asunto, extracto, link_directo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(link_directo) DO UPDATE SET
                    sala = excluded.sala,
                    numero_sentencia = excluded.numero_sentencia,
                    expediente = excluded.expediente,
                    fecha = excluded.fecha,
                    ano = excluded.ano,
                    tema = excluded.tema,
                    materia = excluded.materia,
                    asunto = excluded.asunto,
                    extracto = excluded.extracto,
                    fecha_escaneo = CURRENT_TIMESTAMP
                ''', (
                    decision.get("sala", "Sala Constitucional"),
                    str(decision.get("numero_sentencia", decision.get("sentencia", "S/N"))),
                    str(decision.get("expediente", "S/E")),
                    str(decision.get("fecha", "N/A")),
                    int(decision.get("ano", 2024)),
                    str(decision.get("tema", "Sentencia")),
                    str(decision.get("materia", "Derecho Procesal")),
                    str(decision.get("asunto", "")),
                    str(decision.get("extracto", decision.get("asunto", ""))),
                    str(decision.get("link_directo", decision.get("url", "https://historico.tsj.gob.ve")))
                ))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error inserting decision into SQLite: {e}")
                return False

    def guardar_lote(self, lista_decisiones: List[Dict[str, Any]]) -> int:
        """Saves a batch of decision dictionaries into SQLite."""
        insertados = 0
        for dec in lista_decisiones:
            if self.insertar_o_actualizar(dec):
                insertados += 1
        return insertados

    def obtener_todas(self) -> List[Dict[str, Any]]:
        """Retrieves all indexed decision records from SQLite."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM decisiones ORDER BY ano DESC, id DESC")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def buscar_por_criterio(self, query: str = "", sala: str = "", ano: Optional[int] = None) -> List[Dict[str, Any]]:
        """Searches decision records in SQLite database by query, chamber, or year."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            sql = "SELECT * FROM decisiones WHERE 1=1"
            params = []

            if query.strip():
                kw = f"%{query.strip()}%"
                sql += " AND (asunto LIKE ? OR extracto LIKE ? OR tema LIKE ? OR materia LIKE ? OR expediente LIKE ? OR numero_sentencia LIKE ?)"
                params.extend([kw, kw, kw, kw, kw, kw])

            if sala.strip():
                sql += " AND sala LIKE ?"
                params.append(f"%{sala.strip()}%")

            if ano:
                sql += " AND ano = ?"
                params.append(ano)

            sql += " ORDER BY ano DESC, id DESC"
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Returns summary statistics of SQLite database records."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM decisiones")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT sala, count(*) as cant FROM decisiones GROUP BY sala ORDER BY cant DESC")
            por_sala = {row["sala"]: row["cant"] for row in cursor.fetchall()}

            cursor.execute("SELECT ano, count(*) as cant FROM decisiones GROUP BY ano ORDER BY ano DESC")
            por_ano = {row["ano"]: row["cant"] for row in cursor.fetchall()}

            return {
                "total_registros": total,
                "por_sala": por_sala,
                "por_ano": por_ano,
                "db_path": os.path.abspath(self.db_path)
            }

    @staticmethod
    def listar_todas_las_bases_de_datos(base_dir: str = "data/Databases_SQLite") -> List[Dict[str, Any]]:
        """Scans the database directory and returns statistics for each search database."""
        if not os.path.exists(base_dir):
            return []
        
        db_files = [f for f in os.listdir(base_dir) if f.endswith(".db")]
        res = []
        for db_file in sorted(db_files):
            full_path = os.path.join(base_dir, db_file)
            try:
                mgr = TSJDatabaseManager(db_path=full_path)
                stats = mgr.obtener_estadisticas()
                stats["filename"] = db_file
                res.append(stats)
            except Exception as e:
                res.append({"filename": db_file, "error": str(e), "total_registros": 0})
        return res

