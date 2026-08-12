@echo off
chcp 65001 > nul
title Case Law Extractor powered by sha256.us - Dashboard Web

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Verificar instalacion de Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no se encuentra en el PATH.
    pause
    exit /b 1
)

cls
echo ===============================================================================
echo   Case Law Extractor powered by sha256.us
echo   Iniciando entorno local y abriendo interfaz web en navegador...
echo ===============================================================================
echo.
echo  Servidor Web 100%% Python activo en: http://127.0.0.1:8050/
echo.

python main.py --dash

pause
