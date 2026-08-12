"""Script to generate Windows batch files with CRLF line endings."""

bat_content = """@echo off
chcp 65001 > nul
title Extractor de Jurisprudencias - TSJ Venezuela

REM Verificar instalacion de Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no se encuentra en el PATH.
    pause
    exit /b 1
)

if "%~1"=="1" goto MODO_TECNOLOGIA
if "%~1"=="--tech" goto MODO_TECNOLOGIA
if "%~1"=="2" goto MODO_ESTANDAR
if "%~1"=="3" goto MODO_PRUEBAS
if "%~1"=="4" goto SALIR

cls
echo ===========================================================================
echo       SISTEMA DE EXTRACCION DE JURISPRUDENCIA - TSJ VENEZUELA
echo  Modulo Especializado: Pruebas Digitales, Delitos Informaticos y Tecnologia
echo ===========================================================================
echo.

:MENU
echo Seleccione la opcion deseada:
echo.
echo   [1] Escaneo Multisala: Pruebas Digitales, Delitos Informaticos y Tecnologia (Todas las Salas)
echo   [2] Extraccion Estandar (Segun config.json)
echo   [3] Ejecutar Pruebas del Sistema (Unit Tests)
echo   [4] Salir
echo.
set /p OPCION="Ingrese el numero de opcion (1-4): "

if "%OPCION%"=="1" goto MODO_TECNOLOGIA
if "%OPCION%"=="2" goto MODO_ESTANDAR
if "%OPCION%"=="3" goto MODO_PRUEBAS
if "%OPCION%"=="4" goto SALIR

echo.
echo [Opcion Invalida] Por favor ingrese un numero del 1 al 4.
echo.
goto MENU

:MODO_TECNOLOGIA
cls
echo ===========================================================================
echo  Iniciando Escaneo Multisala: Pruebas Digitales, Delitos Informaticos...
echo ===========================================================================
echo.
python main.py --modo-tecnologia
goto FIN

:MODO_ESTANDAR
cls
echo ===========================================================================
echo  Iniciando Extraccion Estandar segun config.json...
echo ===========================================================================
echo.
python main.py config.json
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
