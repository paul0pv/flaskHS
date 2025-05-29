#!/bin/bash

# Este script automatiza la configuración del entorno virtual
# e inicia el servidor Flask

# Directorio base del script (donde se encuentra start.sh)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Rutas esperadas para el entorno virtual y el script principal del servidor
VENV_PATH="$SCRIPT_DIR/webenv"
RUN_PY_PATH="$SCRIPT_DIR/server/run.py" 

# --- Paso 1: Verificar e instalar pyenv si no existe (opcional, pero buena práctica) ---
# Si usas pyenv para gestionar versiones de Python, esto es útil.
# Si solo usas el Python del sistema o de Termux, puedes omitir esta sección
# y simplemente asegurarte de tener 'python3' y 'pip' instalados.
# Por simplicidad, este script asume que Python y pip ya están disponibles.
# Para Termux: pkg install python python-pip

# --- Paso 2: Crear el entorno virtual si no existe ---
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment at $VENV_PATH..."
    python3 -m venv "$VENV_PATH"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
fi

# --- Paso 3: Activar el entorno virtual ---
echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate the virtual environment."
    exit 1
fi

# --- Paso 4: Instalar/Actualizar dependencias ---
echo "Installing/Updating dependencies from requirements.txt..."
# Asegúrate de que requirements.txt está en el mismo directorio que start.sh
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip install -r "$SCRIPT_DIR/requirements.txt"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies."
        deactivate # Desactivar el venv antes de salir
        exit 1
    fi
else
    echo "Warning: requirements.txt not found at $SCRIPT_DIR/requirements.txt. Skipping dependency installation."
fi

# --- Paso 5: Verificar que run.py exista ---
if [ ! -f "$RUN_PY_PATH" ]; then
    echo "Error: run.py not found at $RUN_PY_PATH. Please ensure it's in the correct directory."
    deactivate
    exit 1
fi

# --- Paso 6: Iniciar el servidor Flask ---
echo "Starting Flask server with run.py..."
python "$RUN_PY_PATH"

# --- Paso 7: Desactivar el entorno virtual al finalizar el script ---
# Esto se ejecutará una vez que el servidor se detenga (por ejemplo, con Ctrl+C)
echo "Deactivating virtual environment."
deactivate
