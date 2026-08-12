@echo off
title Escaneo Global de Jurisprudencia TSJ (2019-2026) - SQLite DB y Excel

REM Verificar instalacion de Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no se encuentra en el PATH.
    pause
    exit /b 1
)

if "%~1"=="1" goto MODO_ESCANEO_GLOBAL
if "%~1"=="--global" goto MODO_ESCANEO_GLOBAL
if "%~1"=="-g" goto MODO_ESCANEO_GLOBAL
if "%~1"=="--escaneo-global" goto MODO_ESCANEO_GLOBAL
if "%~1"=="2" goto MODO_ACTUALIZAR
if "%~1"=="3" goto MODO_BUSQUEDA_PERSONALIZADA
if "%~1"=="4" goto MODO_STATS
if "%~1"=="5" goto MODO_PASO_A_PASO
if "%~1"=="6" goto MODO_PRUEBAS
if "%~1"=="7" goto SALIR

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
echo   [6] INICIAR DASHBOARD WEB EN TIEMPO REAL (http://localhost:8080/gui/index.html)
echo   [7] Ejecutar Pruebas del Sistema (Unit Tests)
echo   [8] Salir
echo.
set /p OPCION="Ingrese el numero de opcion (1-8): "

if "%OPCION%"=="1" goto MODO_ESCANEO_GLOBAL
if "%OPCION%"=="2" goto MODO_ACTUALIZAR
if "%OPCION%"=="3" goto MODO_BUSQUEDA_PERSONALIZADA
if "%OPCION%"=="4" goto MODO_STATS
if "%OPCION%"=="5" goto MODO_PASO_A_PASO
if "%OPCION%"=="6" goto MODO_WEB
if "%OPCION%"=="7" goto MODO_PRUEBAS
if "%OPCION%"=="8" goto SALIR

echo.
echo [Opcion Invalida] Por favor ingrese un numero del 1 al 8.
echo.
goto MENU

:MODO_WEB
cls
echo ===========================================================================
echo  Iniciando Dashboard Web en Tiempo Real (DC3 Cyber Center Style)...
echo  Abra en su navegador: http://localhost:8080/gui/index.html
echo ===========================================================================
echo.
start http://localhost:8080/gui/index.html
python main.py --web
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
echo ===========================================================================
echo  Sincronizando Base de Datos SQLite y Generando Excel (.xlsx)...
echo ===========================================================================
echo.
python main.py --actualizar
goto FIN

:MODO_BUSQUEDA_PERSONALIZADA
cls
echo ===========================================================================
echo  Iniciando Busqueda Personalizada (SQLite DB + Excel)...
echo ===========================================================================
echo.
python main.py
goto FIN

:MODO_STATS
cls
echo ===========================================================================
echo  Consultando Estadisticas de la Base de Datos SQLite...
echo ===========================================================================
echo.
python main.py --stats
goto FIN

:MODO_PASO_A_PASO
cls
echo ===========================================================================
echo  Iniciando Extraccion Guiada Paso a Paso con Impresion PDF...
echo ===========================================================================
echo.
python main.py --paso-a-paso
goto FIN

:MODO_PRUEBAS
cls
echo ===========================================================================
echo  Ejecutando Suite de Pruebas Unitarias...
echo ===========================================================================
echo.
python -m unittest tests/test_extractor.py
goto FIN

:FIN
echo.
echo ===========================================================================
echo [OK] Proceso finalizado. Registros guardados en data/tsj_jurisprudencia.db
echo ===========================================================================
echo.
pause
exit /b 0

:SALIR
exit /b 0
