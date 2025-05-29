from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import requests # Para enviar comandos al microcontrolador
import json 

from database import (
    init_db,
    get_led_state,
    update_led_state,
    get_latest_sensor_data,
    insert_sensor_data,
    register_device, 
    get_all_devices 
)

app = Flask(__name__)

# Configuración de Flask-SocketIO 
socketio = SocketIO(app)
#socketio = SocketIO(app, async_mode='eventlet') # Asegurar el modo asíncrono si se usa eventlet

# --- CONFIGURACIÓN DE LA APLICACIÓN ---
# Considerar externalizar estas configuraciones (ej. en un archivo config.py o variables de entorno)
# Para este ejemplo, dejaremos un placeholder y una nota para el futuro.
MICROCONTROLLER_DEFAULT_URL = "http://192.168.1.100" 
# Nota: En un sistema más robusto, la URL se obtendría del registro de dispositivos.

# --- RUTAS DE FLASK ---
@app.route("/")
def index():
    """
    Renderiza la plantilla principal del dashboard.
    """
    return render_template("index.html")

@app.route("/api/register-device", methods=["POST"])
def register_device_api():
    """
    Endpoint para que los microcontroladores se registren o actualicen su información.
    Los datos esperados son {"name": "ESP32_Node1", "ip": "192.168.1.100", "type": "ESP32"}.
    """
    try:
        data = request.get_json()
        if not all(k in data for k in ("name", "ip", "type")):
            return jsonify({"status": "error", "message": "Missing required fields (name, ip, type)"}), 400

        # Llama a la función de la base de datos para registrar/actualizar el dispositivo
        register_device(data["name"], data["ip"], data["type"])

        return jsonify({"status": "registered", "message": f"Device {data['name']} registered/updated."}), 200
    except Exception as e:
        print(f"Error registering device: {e}")
        return jsonify({"status": "error", "message": f"Could not register device: {e}"}), 500

@app.route("/api/sensor", methods=["POST"])
def update_sensor_data():
    """
    Endpoint para que los microcontroladores envíen datos de sensores.
    Los datos esperados son {"device": "ESP32", "sensors": [{"type": "light", "value": 23.7}, ...]}.    
    """
    try:
        data = request.get_json()
        # Validar la estructura del payload
        if not all(k in data for k in ("device", "sensors")):
            return jsonify({"status": "error", "message": "Missing required sensor data fields (device, sensors)"}), 400
        
        device = data["device"]
        sensors = data["sensors"]
        
        for sensor in sensors:
            if not all(k in sensor for k in ("type","value")):
                return jsonify({"status": "error", "message": "Each sensor must have 'type' and 'value' fields"}), 400
        # Insertar los datos en la base de datos
        # Se asume que 'device' en el payload es el 'device_name'
            insert_sensor_data(device, sensor["type"], sensor["value"])

        # Emitir los datos a todos los clientes de Socket.IO conectados
        socketio.emit("sensor_update", data, namespace="/")
        return jsonify({"status": "success", "message": "Sensor data received and processed."}), 200
    except Exception as e:
        print(f"Error processing sensor data: {e}")
        return jsonify({"status": "error", "message": f"Error processing sensor data: {e}"}), 500

# --- EVENTOS DE SOCKET.IO ---
@socketio.on("connect")
def on_connect():
    """
    Se ejecuta cuando un cliente de Socket.IO se conecta.
    Envía el estado actual de los LEDs al cliente.
    """
    state = get_led_state()
    emit("led_update", state)
    print("Client connected, LED state sent:", state)

@socketio.on("control_led")
def on_control_led(data):
    """
    Maneja los comandos de control de LEDs desde el frontend.
    Actualiza el estado en la DB, envía la petición al microcontrolador y emite el estado actualizado.
    """
    if not isinstance(data, dict) or "ledRed" not in data or "ledGreen" not in data:
        print("Invalid LED control data received:", data)
        return

    update_led_state(data) # Actualiza el estado en la base de datos

    # Contactar al microcontrolador para actualizar el estado físico de los LEDs
    # En un sistema multi-dispositivo, se debería buscar la IP del dispositivo específico
    # en la tabla 'devices'. Para este PoC, se usa una URL por defecto.
    target_ip = MICROCONTROLLER_DEFAULT_URL # Usar la URL configurable

    try:
        # Asegurarse de que la URL termina en /api/control-led para el ESP32
        requests.post(f"{target_ip}/api/control-led", json=data)
        print(f"Command sent to ESP32: {target_ip}/api/control-led, data: {data}")
    except requests.exceptions.ConnectionError as e:
        print(f"Failed to contact microcontrollers at {target_ip}: {e}")
        # Considerar emitir un evento de error al frontend para notificar al usuario.
        emit("server_message", {"type": "error", "text": f"Failed to contact microcontrollers: {e}"}, broadcast=True)
    except Exception as e:
        print(f"An unexpected error occurred while sending LED command: {e}")
        emit("server_message", {"type": "error", "text": f"Unexpected error controlling LED: {e}"}, broadcast=True)


    # Emitir la actualización a todos los clientes de Socket.IO conectados
    emit("led_update", data, broadcast=True)


# --- FUNCIÓN PRINCIPAL DE EJECUCIÓN ---
if __name__ == "__main__":
    # Inicializa la base de datos al inicio de la aplicación
    print("Initializing database...")
    init_db()
    print("Database initialized.")

    # Inicia el servidor Flask-SocketIO
    # ¡ADVERTENCIA! debug=True NO DEBE USARSE EN PRODUCCIÓN por razones de seguridad y rendimiento.
    print("Starting Flask-SocketIO server...")
# 'allow_unsafe_werkzeug=True' será necesario para ejecutar Werkzeug en 0.0.0.0 en entornos como Termux
# pero igualmente NO DEBE USARSE EN PRODUCCIÓN.
#   socketio.run(app, host="0.0.0.0", port=5000, debug=True, allow_unsafe_werkzeug=True)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
