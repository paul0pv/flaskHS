# start.ps1
# Script para iniciar el servidor Flask en un entorno Windows (PowerShell)

# Obtiene la ruta del directorio donde se encuentra este script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Define las rutas relativas al directorio del script
$VenvPath = Join-Path $ScriptDir "webenv\Scripts\Activate.ps1"
$RunPyPath = Join-Path $ScriptDir "server\run.py" # O "server\run-mqtt.py" si usas MQTT

# --- Validación de rutas ---
if (-not (Test-Path $VenvPath)) {
    Write-Host "Error: Entorno virtual no encontrado en $VenvPath" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $RunPyPath)) {
    Write-Host "Error: run.py no encontrado en $RunPyPath" -ForegroundColor Red
    Write-Host "Asegúrate de que run.py (o run-mqtt.py) exista y la ruta sea correcta." -ForegroundColor Yellow
    exit 1
}

# --- Activar el entorno virtual ---
Write-Host "Activando el entorno virtual..." -ForegroundColor Cyan
try {
    . $VenvPath
    if ($LASTEXITCODE -ne 0) {
        throw "Error al activar el entorno virtual. Código de salida: $LASTEXITCODE"
    }
} catch {
    Write-Host "Error activando el entorno virtual: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# --- Iniciar el servidor Flask ---
Write-Host "Iniciando el servidor Flask..." -ForegroundColor Green
try {
    python $RunPyPath

    # NOTA: Después de ejecutar el script Python, la ejecución de PowerShell continuará.
    # El entorno virtual permanecerá activo en esta ventana de PowerShell hasta que la cierres
    # o ejecutes 'deactivate'.
} catch {
    Write-Host "Error al ejecutar run.py: $($_.Exception.Message)" -ForegroundColor Red
    # No se hace 'deactivate' aquí automáticamente, ya que la ventana de PowerShell
    # podría usarse para depuración.
    exit 1
}

Write-Host "El script ha terminado. El entorno virtual permanece activo." -ForegroundColor DarkGreen
Write-Host "Para desactivar el entorno virtual, escribe 'deactivate'." -ForegroundColor DarkCyan
