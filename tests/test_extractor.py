"""
Unit and Integration tests for Extractor Jurisprudencias.
"""

import os
import shutil
import unittest
from src.utils import (
    load_config,
    save_config,
    clean_text,
    parse_jurisprudencia_html,
    export_to_json,
    export_to_csv,
    export_to_excel,
    generate_decision_pdf,
    export_summary_pdf,
    sanitize_search_name,
    prompt_select_sala,
    prompt_select_mes
)
from src.extractor import JurisprudenciaExtractor


class TestJurisprudenciaExtractor(unittest.TestCase):

    def setUp(self):
        self.test_dir = "data/test_output"
        os.makedirs(self.test_dir, exist_ok=True)
        self.sample_decision = {
            "numero_sentencia": "0123",
            "expediente": "AA50-T-2024-000123",
            "fecha": "15 de enero de 2024",
            "ponente": "Dra. Tania D'Amelio",
            "asunto": "Acción de Amparo Constitucional",
            "sala": "Sala Constitucional",
            "categoria": "Pruebas Digitales",
            "url": "http://historico.tsj.gob.ve/decisiones/scon/enero/0123.html",
            "resumen": "Se declara con lugar la acción de amparo ejercida por el ciudadano.",
            "texto_completo": "SENTENCIA N° 0123\nExpediente: AA50-T-2024-000123\nMagistrado Ponente: Dra. Tania D'Amelio\n\nI. ANTECEDENTES..."
        }

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_load_and_save_config(self):
        config_path = os.path.join(self.test_dir, "test_config.json")
        data = {"sala": "Sala Político-Administrativa", "limite": 5}
        save_config(data, config_path)
        loaded = load_config(config_path)
        self.assertEqual(loaded["sala"], "Sala Político-Administrativa")
        self.assertEqual(loaded["limite"], 5)

    def test_html_parsing(self):
        sample_html = """
        <html>
            <body>
                <h1>TRIBUNAL SUPREMO DE JUSTICIA</h1>
                <p>Sentencia Nº 0890</p>
                <p>Expediente: AA50-X-2024-000099</p>
                <p>Magistrado Ponente: Dra. Tania D'Amelio</p>
                <p>Fecha: 20 de mayo de 2024</p>
                <p>Texto completo del fallo constitucional en materia de garantías procesales y prueba digital.</p>
            </body>
        </html>
        """
        parsed = parse_jurisprudencia_html(sample_html, "http://test.url")
        self.assertEqual(parsed["numero_sentencia"], "0890")
        self.assertEqual(parsed["expediente"], "AA50-X-2024-000099")
        self.assertIn("Tania", parsed["ponente"])

    def test_exporters(self):
        data = [self.sample_decision]
        
        # Test JSON
        json_path = os.path.join(self.test_dir, "test.json")
        export_to_json(data, json_path)
        self.assertTrue(os.path.exists(json_path))

        # Test CSV
        csv_path = os.path.join(self.test_dir, "test.csv")
        export_to_csv(data, csv_path)
        self.assertTrue(os.path.exists(csv_path))

        # Test Excel
        xlsx_path = os.path.join(self.test_dir, "test.xlsx")
        export_to_excel(data, xlsx_path)
        self.assertTrue(os.path.exists(xlsx_path))

        # Test Individual PDF
        pdf_path = os.path.join(self.test_dir, "test_sentencia.pdf")
        generate_decision_pdf(self.sample_decision, pdf_path)
        self.assertTrue(os.path.exists(pdf_path))

        # Test Summary PDF
        summary_pdf_path = os.path.join(self.test_dir, "test_summary.pdf")
        export_summary_pdf(data, summary_pdf_path)
        self.assertTrue(os.path.exists(summary_pdf_path))

    def test_tech_scan_all_salas(self):
        extractor = JurisprudenciaExtractor(config_dict={
            "carpeta_tecnologia": self.test_dir,
            "timeout": 2,
            "max_retries": 1
        })
        results = extractor.run_tech_scan_all_salas()
        self.assertGreaterEqual(len(results), 7)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "Jurisprudencia_Tecnologia_Todas_Salas.json")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "Jurisprudencia_Tecnologia_Todas_Salas.xlsx")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "Jurisprudencia_Tecnologia_Todas_Salas.csv")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "Resumen_Jurisprudencia_Tecnologia_Todas_Salas.pdf")))

    def test_paso_a_paso_flow(self):
        extractor = JurisprudenciaExtractor(config_dict={
            "carpeta_tecnologia": self.test_dir,
            "timeout": 2,
            "max_retries": 1
        })
        results = extractor.run_paso_a_paso(salas=["casacion_penal", "constitucional"])
        self.assertGreaterEqual(len(results), 3)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "Resumen_Jurisprudencia_Paso_A_Paso.pdf")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "jurisprudencia_paso_a_paso.json")))

    def test_buscador_excel(self):
        extractor = JurisprudenciaExtractor(config_dict={
            "carpeta_excel": self.test_dir
        })
        excel_path = extractor.run_buscador_excel(palabra_clave="Tecnología")
        self.assertTrue(os.path.exists(excel_path))

    def test_actualizar_jurisprudencias(self):
        extractor = JurisprudenciaExtractor(config_dict={
            "carpeta_excel": self.test_dir
        })
        excel_path = extractor.run_actualizar_jurisprudencias(ano_inicio=2019, ano_fin=2026)
        self.assertTrue(os.path.exists(excel_path))

    def test_sqlite_database(self):
        from src.database import TSJDatabaseManager
        db_path = os.path.join(self.test_dir, "test_tsj.db")
        db = TSJDatabaseManager(db_path=db_path)
        
        test_rec = {
            "sala": "Sala de Casación Civil",
            "numero_sentencia": "05",
            "expediente": "99-609",
            "fecha": "Jueves, 17 de Febrero de 2000",
            "ano": 2000,
            "tema": "Técnica del escrito de formalización",
            "materia": "Derecho Procesal Civil",
            "asunto": "Escrito de formalización. Reposición no decretada.",
            "extracto": "La reposición no decretada debe desarrollarse en el escrito de formalización...",
            "link_directo": "https://historico.tsj.gob.ve/decisiones/scc/febrero/05-170200-99609.HTM"
        }
        db.insertar_o_actualizar(test_rec)
        stats = db.obtener_estadisticas()
        self.assertEqual(stats["total_registros"], 1)

    def test_escaneo_global(self):
        extractor = JurisprudenciaExtractor(config_dict={
            "carpeta_excel": self.test_dir
        })
        excel_path = extractor.run_escaneo_global(ano_inicio=2019, ano_fin=2026)
        self.assertTrue(os.path.exists(excel_path))

    def test_dynamic_db_and_excel_naming(self):
        sanitized = sanitize_search_name("Delitos Informáticos (2024)", prefix="Busqueda")
        self.assertEqual(sanitized, "Busqueda_Delitos_Informaticos_2024")
        
        extractor = JurisprudenciaExtractor(config_dict={
            "carpeta_excel": self.test_dir
        })
        excel_path = extractor.run_actualizar_jurisprudencias(palabra_clave="Evidencia Digital", ano_inicio=2019, ano_fin=2026)
        self.assertTrue(os.path.exists(excel_path))
        self.assertIn("Busqueda_Evidencia_Digital", excel_path)
        self.assertTrue(os.path.exists("data/Databases_SQLite/Busqueda_Evidencia_Digital.db"))

    def test_sala_and_mes_filtering(self):
        extractor = JurisprudenciaExtractor(config_dict={
            "carpeta_excel": self.test_dir
        })
        sala_choice = {"key": "casacion_civil", "nombre": "Sala de Casación Civil", "code": "scc"}
        mes_choice = {"key": "febrero", "nombre": "Febrero", "code": "febrero"}
        
        excel_path = extractor.run_escaneo_global(
            ano_inicio=2019,
            ano_fin=2026,
            sala_info=sala_choice,
            mes_info=mes_choice
        )
        self.assertTrue(os.path.exists(excel_path))
        self.assertIn("Escaneo_SCC_Febrero", excel_path)
        self.assertTrue(os.path.exists("data/Databases_SQLite/Escaneo_SCC_Febrero_2019_2026.db"))


if __name__ == "__main__":
    unittest.main()
