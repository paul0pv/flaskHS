:: start.cmd
:: Script para iniciar el servidor Flask en un entorno Windows (Símbolo del Sistema)

@echo off
setlocal

:: Obtiene la ruta del directorio donde se encuentra este script
set "SCRIPT_DIR=%~dp0"

:: Define las rutas relativas al directorio del script
set "VENV_PATH=%SCRIPT_DIR%webenv\Scripts\activate.bat"
set "RUN_PY_PATH=%SCRIPT_DIR%server\run.py" :: O "server\run-mqtt.py" si usas MQTT

:: --- Validación de rutas ---
if not exist "%VENV_PATH%" (
    echo Error: Entorno virtual no encontrado en %VENV_PATH%
    goto :eof
)

if not exist "%RUN_PY_PATH%" (
    echo Error: run.py no encontrado en %RUN_PY_PATH%
    echo Asegurate de que run.py o run-mqtt.py exista y la ruta sea correcta.
    goto :eof
)

:: --- Activar el entorno virtual ---
echo Activando el entorno virtual...
call "%VENV_PATH%"
if %errorlevel% neq 0 (
    echo Error activando el entorno virtual.
    goto :eof
)

:: --- Iniciar el servidor Flask ---
echo Iniciando el servidor Flask...
python "%RUN_PY_PATH%"

:: NOTA: Cuando el script python termina, este script cmd continuará.
:: El entorno virtual se desactivará automaticamente al final del script.

echo El script ha terminado.
deactivate

endlocal
