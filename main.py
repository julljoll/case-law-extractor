"""
Interactive CLI and Entry Point for Buscador e Indizador TSJ a SQLite DB y Excel.
Searches real jurisprudence decisions from 2019 to present date on TSJ Venezuela portal,
storing all scraped fields (including extract popup details and direct links) in SQLite DB and Excel.
"""

import sys
import os
from colorama import init, Fore, Style
from src.extractor import JurisprudenciaExtractor
from src.utils import load_config

init(autoreset=True)

def print_banner():
    print(f"{Fore.CYAN}{'='*75}")
    print(f"{Fore.CYAN}       BUSCADOR Y BASE DE DATOS DE JURISPRUDENCIA TSJ VENEZUELA")
    print(f"{Fore.CYAN}  Escaneo Global (2019-2026) a SQLite DB Local + Matriz Excel (.xlsx)")
    print(f"{Fore.CYAN}{'='*75}{Style.RESET_ALL}\n")

def show_menu():
    print(f"{Fore.YELLOW}Seleccione la opción deseada:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}[1]{Style.RESET_ALL} Escaneo Global de Todas las Páginas del TSJ (2019 a 2026) -> SQLite + Excel")
    print(f"  {Fore.GREEN}[2]{Style.RESET_ALL} Actualizar Base de Datos SQLite y Excel (Últimas Jurisprudencias)")
    print(f"  {Fore.GREEN}[3]{Style.RESET_ALL} Búsqueda Personalizada por Palabra Clave, Materia o Expediente (SQLite + Excel)")
    print(f"  {Fore.GREEN}[4]{Style.RESET_ALL} Ver Estadísticas y Registros de la Base de Datos SQLite Local")
    print(f"  {Fore.GREEN}[5]{Style.RESET_ALL} Extracción Guiada Paso a Paso (Ventana Emergente e Impresión PDF)")
    print(f"  {Fore.GREEN}[6]{Style.RESET_ALL} Salir\n")

def main():
    print_banner()
    
    # Check CLI arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--escaneo-global", "--global", "-g", "1"]:
            print(f"{Fore.CYAN}Ejecutando Escaneo Global de Todas las Páginas del TSJ (2019 - 2026)...{Style.RESET_ALL}")
            extractor = JurisprudenciaExtractor()
            extractor.run_escaneo_global(ano_inicio=2019, ano_fin=2026)
            return
        elif arg in ["--actualizar", "--ultimas", "-u", "2"]:
            print(f"{Fore.CYAN}Ejecutando Sincronización de Últimas Jurisprudencias...{Style.RESET_ALL}")
            extractor = JurisprudenciaExtractor()
            extractor.run_actualizar_jurisprudencias(ano_inicio=2019, ano_fin=2026)
            return
        elif arg in ["--stats", "--db", "4"]:
            extractor = JurisprudenciaExtractor()
            extractor.run_consultar_db_stats()
            return
        elif arg in ["--paso-a-paso", "-p", "paso_a_paso", "5"]:
            print(f"{Fore.CYAN}Ejecutando Modo Paso a Paso con Impresión a PDF...{Style.RESET_ALL}")
            extractor = JurisprudenciaExtractor()
            extractor.run_paso_a_paso()
            return
        elif os.path.exists(sys.argv[1]):
            extractor = JurisprudenciaExtractor(config_path=sys.argv[1])
            extractor.run_escaneo_global()
            return

    # Check if executed interactively
    show_menu()
    
    try:
        if sys.stdin.isatty():
            opcion = input("Ingrese el número de opción (1-6): ").strip()
            if opcion == "1":
                extractor = JurisprudenciaExtractor()
                extractor.run_escaneo_global(ano_inicio=2019, ano_fin=2026)
            elif opcion == "2":
                extractor = JurisprudenciaExtractor()
                extractor.run_actualizar_jurisprudencias(ano_inicio=2019, ano_fin=2026)
            elif opcion == "3":
                kw = input("Ingrese la palabra clave, delito, materia o número de expediente: ").strip()
                extractor = JurisprudenciaExtractor()
                extractor.run_actualizar_jurisprudencias(palabra_clave=kw, ano_inicio=2019, ano_fin=2026)
            elif opcion == "4":
                extractor = JurisprudenciaExtractor()
                extractor.run_consultar_db_stats()
            elif opcion == "5":
                extractor = JurisprudenciaExtractor()
                extractor.run_paso_a_paso()
            elif opcion == "6":
                print("Saliendo...")
                sys.exit(0)
            else:
                print(f"{Fore.YELLOW}Opción no reconocida. Ejecutando Escaneo Global por defecto...{Style.RESET_ALL}")
                extractor = JurisprudenciaExtractor()
                extractor.run_escaneo_global(ano_inicio=2019, ano_fin=2026)
        else:
            print(f"{Fore.CYAN}[AUTO] Ejecutando Escaneo Global de todas las páginas del TSJ (2019-2026)...{Style.RESET_ALL}")
            extractor = JurisprudenciaExtractor()
            extractor.run_escaneo_global(ano_inicio=2019, ano_fin=2026)
    except Exception as e:
        print(f"{Fore.CYAN}[AUTO] Ejecutando Escaneo Global de todas las páginas del TSJ (2019-2026)...{Style.RESET_ALL}")
        extractor = JurisprudenciaExtractor()
        extractor.run_escaneo_global(ano_inicio=2019, ano_fin=2026)

if __name__ == "__main__":
    main()
