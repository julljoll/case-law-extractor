"""
Interactive CLI and Entry Point for Buscador e Indizador TSJ a SQLite DB y Excel.
Searches real jurisprudence decisions from 2019 to present date on TSJ Venezuela portal,
storing all scraped fields (including extract popup details and direct links) in SQLite DB and Excel.
"""

import sys
import os
from colorama import init, Fore, Style
from src.extractor import JurisprudenciaExtractor
from src.utils import load_config, prompt_select_sala, prompt_select_mes

init(autoreset=True)

def print_banner():
    print(f"{Fore.BLUE}{'='*78}")
    print(f"{Fore.YELLOW}  [ TSJ CYBER FORENSICS LAB ] {Fore.CYAN}Case Law Extractor powered by sha256.us")
    print(f"{Fore.WHITE}       Dashboard en Tiempo Real TSJ Venezuela")
    print(f"{Fore.YELLOW}    Generación de BD SQLite + Excel Dedicados por Fórmula de Búsqueda")
    print(f"{Fore.BLUE}{'='*78}{Style.RESET_ALL}\n")

def show_menu():
    print(f"{Fore.YELLOW}▸ SELECCIONE LA OPCIÓN DE OPERACIÓN (DC3 SYSTEM TACTICAL MENU):{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}[1]{Style.RESET_ALL} Escaneo Global / Específico de Páginas del TSJ ➔ Escaneo_<Sala>_<Mes>.db + .xlsx")
    print(f"  {Fore.YELLOW}[2]{Style.RESET_ALL} Actualizar Base de Datos de Últimas Jurisprudencias ➔ Actualizacion.db + .xlsx")
    print(f"  {Fore.YELLOW}[3]{Style.RESET_ALL} Búsqueda por Fórmula / Palabra Clave / Expediente ➔ Genera BD SQLite + Excel Dedicados")
    print(f"  {Fore.YELLOW}[4]{Style.RESET_ALL} Inspeccionar Estadísticas de Todas las Bases de Datos SQLite Generadas")
    print(f"  {Fore.YELLOW}[5]{Style.RESET_ALL} Extracción Guiada Paso a Paso (Ventana Emergente e Impresión PDF)")
    print(f"  {Fore.GREEN}[6] INICIAR DASHBOARD WEB 100% PYTHON (http://127.0.0.1:8050/ - Dash + Bootstrap){Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}[7]{Style.RESET_ALL} Salir\n")

def main():
    print_banner()
    
    # Check CLI arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--dash", "--web", "--dashboard", "--gui", "6"]:
            from gui.dash_app import run_dash_app
            run_dash_app()
            return
        elif arg in ["--escaneo-global", "--global", "-g", "1"]:
            sala_choice = prompt_select_sala()
            mes_choice = prompt_select_mes()
            print(f"{Fore.CYAN}Ejecutando Escaneo TSJ para {sala_choice['nombre']} | Período: {mes_choice['nombre']}...{Style.RESET_ALL}")
            extractor = JurisprudenciaExtractor()
            extractor.run_escaneo_global(ano_inicio=2019, ano_fin=2026, sala_info=sala_choice, mes_info=mes_choice)
            return
        elif arg in ["--actualizar", "--ultimas", "-u", "2"]:
            sala_choice = prompt_select_sala()
            mes_choice = prompt_select_mes()
            print(f"{Fore.CYAN}Ejecutando Sincronización para {sala_choice['nombre']} | Período: {mes_choice['nombre']}...{Style.RESET_ALL}")
            extractor = JurisprudenciaExtractor()
            extractor.run_actualizar_jurisprudencias(ano_inicio=2019, ano_fin=2026, sala_info=sala_choice, mes_info=mes_choice)
            return
        elif arg in ["--stats", "--db", "4"]:
            extractor = JurisprudenciaExtractor()
            extractor.run_consultar_db_stats()
            return
        elif arg in ["--paso-a-paso", "-p", "paso_a_paso", "5"]:
            sala_choice = prompt_select_sala()
            print(f"{Fore.CYAN}Ejecutando Modo Paso a Paso para {sala_choice['nombre']} con Impresión a PDF...{Style.RESET_ALL}")
            extractor = JurisprudenciaExtractor()
            extractor.run_paso_a_paso(salas=[sala_choice["key"]] if sala_choice["key"] != "todas" else None)
            return
        elif os.path.exists(sys.argv[1]):
            extractor = JurisprudenciaExtractor(config_path=sys.argv[1])
            extractor.run_escaneo_global()
            return

    # Check if executed interactively
    show_menu()
    
    try:
        if sys.stdin.isatty():
            opcion = input("Ingrese el número de opción (1-7): ").strip()
            if opcion == "1":
                sala_choice = prompt_select_sala()
                mes_choice = prompt_select_mes()
                extractor = JurisprudenciaExtractor()
                extractor.run_escaneo_global(ano_inicio=2019, ano_fin=2026, sala_info=sala_choice, mes_info=mes_choice)
            elif opcion == "2":
                sala_choice = prompt_select_sala()
                mes_choice = prompt_select_mes()
                extractor = JurisprudenciaExtractor()
                extractor.run_actualizar_jurisprudencias(ano_inicio=2019, ano_fin=2026, sala_info=sala_choice, mes_info=mes_choice)
            elif opcion == "3":
                kw = input("\nIngrese la palabra clave, fórmula de búsqueda, delito, materia o expediente: ").strip()
                sala_choice = prompt_select_sala()
                mes_choice = prompt_select_mes()
                extractor = JurisprudenciaExtractor()
                extractor.run_actualizar_jurisprudencias(palabra_clave=kw, ano_inicio=2019, ano_fin=2026, sala_info=sala_choice, mes_info=mes_choice)
            elif opcion == "4":
                extractor = JurisprudenciaExtractor()
                extractor.run_consultar_db_stats()
            elif opcion == "5":
                sala_choice = prompt_select_sala()
                extractor = JurisprudenciaExtractor()
                extractor.run_paso_a_paso(salas=[sala_choice["key"]] if sala_choice["key"] != "todas" else None)
            elif opcion == "6":
                from gui.dash_app import run_dash_app
                run_dash_app()
            elif opcion == "7":
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
