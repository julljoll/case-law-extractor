"""
Automated 24-Hour Background Scheduler for Case Law Extractor powered by sha256.us.
Periodically checks Tribunal Supremo de Justicia (TSJ) portal for new jurisprudence updates every 24 hours.
"""

import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional

from src.extractor import JurisprudenciaExtractor
from src.database import TSJDatabaseManager
from src.buscador_tsj_excel import BuscadorTSJExcel
from src.utils import SALAS_CHOICES, MESES_CHOICES


class TSJScheduler:
    """Manages background auto-updater thread running every 24 hours."""
    
    def __init__(self, interval_seconds: int = 86400):
        self.interval_seconds = interval_seconds
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self.last_run: Optional[datetime] = None
        self.last_status: str = "Inactivo"
        self.total_decisiones_actualizadas: int = 0
        
    def start(self):
        """Starts the background 24-hour sync thread if not already running."""
        if self._thread is not None and self._thread.is_alive():
            return
            
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True, name="TSJ-24H-AutoUpdater")
        self._thread.start()
        self.last_status = "Ejecutando en segundo plano (Ciclo: 24h)"

    def stop(self):
        """Stops the background scheduler thread."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=3.0)
        self.last_status = "Detenido"

    def is_running(self) -> bool:
        """Returns True if the background scheduler thread is active."""
        return self._thread is not None and self._thread.is_alive()

    def force_update(self) -> Dict[str, Any]:
        """Triggers an immediate update outside the 24-hour schedule."""
        self.last_status = "Sincronizando de forma inmediata..."
        results = self._ejecutar_sincronizacion()
        self.last_run = datetime.now()
        self.last_status = f"Última sincronización: {self.last_run.strftime('%Y-%m-%d %H:%M:%S')}"
        return results

    def _run_loop(self):
        """Background thread loop that sleeps for 24h between sync runs."""
        while not self._stop_event.is_set():
            try:
                self.last_status = "Ejecutando actualización periódica de 24h..."
                self._ejecutar_sincronizacion()
                self.last_run = datetime.now()
                self.last_status = f"En espera del próximo ciclo de 24h. Última ejecución: {self.last_run.strftime('%Y-%m-%d %H:%M:%S')}"
            except Exception as e:
                self.last_status = f"Error en sincronización 24h: {str(e)}"
                
            # Wait for 24 hours or until stop requested
            wait_time = 0
            while wait_time < self.interval_seconds and not self._stop_event.is_set():
                time.sleep(1)
                wait_time += 1

    def _ejecutar_sincronizacion(self) -> Dict[str, Any]:
        """Executes actual query to TSJ portal for new jurisprudence."""
        try:
            buscador = BuscadorTSJExcel()
            excel_path = buscador.actualizar_ultimas_jurisprudencias(
                palabra_clave="",
                ano_inicio=2019,
                ano_fin=datetime.now().year,
                sala_info=SALAS_CHOICES["0"],
                mes_info=MESES_CHOICES["0"]
            )
            
            db_manager = TSJDatabaseManager()
            stats = db_manager.obtener_estadisticas()
            total_db = stats.get("total_registros", 0)
            self.total_decisiones_actualizadas = total_db
            
            return {
                "status": "success",
                "excel_path": excel_path,
                "total_registros": total_db,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def get_info(self) -> Dict[str, Any]:
        """Returns current scheduler state metadata."""
        return {
            "activo": self.is_running(),
            "intervalo_horas": round(self.interval_seconds / 3600, 1),
            "ultima_ejecucion": self.last_run.strftime("%Y-%m-%d %H:%M:%S") if self.last_run else "Ninguna",
            "estado": self.last_status,
            "total_decisiones_bd": self.total_decisiones_actualizadas
        }


# Global Instance for Web App & CLI
global_scheduler = TSJScheduler(interval_seconds=86400)
