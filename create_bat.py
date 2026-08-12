"""Script to generate Windows batch files with CRLF line endings."""

bat_content = """@echo off
chcp 65001 > nul
title Extractor de Jurisprudencias TSJ Venezuela - DC3 Cyber Lab

REM Verificar instalacion de Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no se encuentra en el PATH.
    pause
    exit /b 1
)

if "%~1"=="1" goto MODO_ESCANEO_GLOBAL
if "%~1"=="2" goto MODO_ACTUALIZAR
if "%~1"=="3" goto MODO_BUSQUEDA
if "%~1"=="4" goto MODO_STATS
if "%~1"=="5" goto MODO_PASO_A_PASO
if "%~1"=="6" goto MODO_DASH_WEB
if "%~1"=="7" goto MODO_PRUEBAS
if "%~1"=="8" goto SALIR

cls
color 0A
echo ===============================================================================
echo   [ TSJ CYBER FORENSICS LAB ] DEPARTMENT OF DEFENSE CYBER CRIME CENTER STYLE
echo      BUSCADOR Y BASE DE DATOS DE JURISPRUDENCIA TSJ VENEZUELA (2019 - 2026)
echo   Generacion de BD SQLite + Matriz Excel (.xlsx) Dedicadas por Formula
echo ===============================================================================
echo.

:MENU
echo Seleccione la opcion deseada:
echo.
echo   [1] Escaneo Global Completo de Todas las Paginas del TSJ (2019 a 2026) (SQLite + Excel)
echo   [2] Actualizar Base de Datos SQLite y Excel (Ultimas Jurisprudencias)
echo   [3] Busqueda Personalizada por Palabra Clave, Materia o Expediente (SQLite + Excel)
echo   [4] Ver Estadisticas y Registros de la Base de Datos SQLite Local
echo   [5] Extraccion Guiada Paso a Paso (Ventana Emergente e Impresion PDF)
echo   [6] INICIAR DASHBOARD WEB 100%% PYTHON (http://127.0.0.1:8050/ - Dash + Bootstrap)
echo   [7] Ejecutar Pruebas del Sistema (Unit Tests)
echo   [8] Salir
echo.
set /p OPCION="Ingrese el numero de opcion (1-8): "

if "%OPCION%"=="1" goto MODO_ESCANEO_GLOBAL
if "%OPCION%"=="2" goto MODO_ACTUALIZAR
if "%OPCION%"=="3" goto MODO_BUSQUEDA
if "%OPCION%"=="4" goto MODO_STATS
if "%OPCION%"=="5" goto MODO_PASO_A_PASO
if "%OPCION%"=="6" goto MODO_DASH_WEB
if "%OPCION%"=="7" goto MODO_PRUEBAS
if "%OPCION%"=="8" goto SALIR

echo.
echo [Opcion Invalida] Por favor ingrese un numero del 1 al 8.
echo.
goto MENU

:MODO_DASH_WEB
cls
echo ===========================================================================
echo  Iniciando Dashboard Web 100%% Python (Dash + Dash Bootstrap Components)...
echo  Abra en su navegador: http://127.0.0.1:8050/
echo ===========================================================================
echo.
start http://127.0.0.1:8050/
python main.py --dash
goto FIN

:MODO_ESCANEO_GLOBAL
cls
echo ===========================================================================
echo  Iniciando Escaneo Global de Todas las Paginas del TSJ (2019 a 2026)...
echo ===========================================================================
echo.
python main.py --escaneo-global
goto FIN

:MODO_ACTUALIZAR
cls
python main.py --actualizar
goto FIN

:MODO_BUSQUEDA
cls
python main.py
goto FIN

:MODO_STATS
cls
python main.py --stats
goto FIN

:MODO_PASO_A_PASO
cls
python main.py --paso-a-paso
goto FIN

:MODO_PRUEBAS
cls
echo ===========================================================================
echo  Ejecutando Suite de Pruebas Unitarias...
echo ===========================================================================
echo.
python -m unittest discover tests
goto FIN

:FIN
echo.
echo ===========================================================================
echo [OK] Proceso finalizado.
echo ===========================================================================
echo.
pause
exit /b 0

:SALIR
exit /b 0
"""

# Standardize CRLF
crlf_content = bat_content.replace('\r\n', '\n').replace('\n', '\r\n')
with open('ejecutar_extractor.bat', 'wb') as f:
    f.write(crlf_content.encode('utf-8'))

run_content = "@echo off\r\ncall ejecutar_extractor.bat %*\r\n"
with open('run.bat', 'wb') as f:
    f.write(run_content.encode('utf-8'))

print("Batch files generated successfully with CRLF endings.")
