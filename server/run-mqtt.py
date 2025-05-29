# run-mqtt.py
# Servidor Flask con integración MQTT para recibir datos de sensores y controlar LEDs.

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import requests
import paho.mqtt.client as mqtt
import json
import time # Posible reintento de conexión MQTT

from database import init_db, get_led_state, update_led_state, insert_sensor_data

app = Flask(__name__)
socketio = SocketIO(app)

# --- CONFIGURACIÓN DE PARÁMETROS ---
# IP del microcontrolador (usado para control directo de LEDs via HTTP)
# ¡IMPORTANTE: Reemplaza con la IP real de tu microcontrolador!
MICRO_IP = "http://192.168.1.100"

# Configuración del Broker MQTT
MQTT_BROKER_URL = "localhost" # O la IP de tu broker MQTT (ej. "192.168.1.100")
MQTT_BROKER_PORT = 1883
MQTT_PUB_TOPIC = "commands/esp32" # Tópico para enviar comandos al ESP32 (ej. LEDs)
MQTT_SUB_TOPIC = "sensors/data"   # Tópico donde el ESP32 publica los datos de sensores

# Cliente MQTT global
mqtt_client = None

# --- Funciones de Callbacks MQTT ---

def on_connect(client, userdata, flags, rc):
    """Callback que se ejecuta cuando el cliente MQTT se conecta al broker."""
    if rc == 0:
        print(f"MQTT: Conectado al broker en {MQTT_BROKER_URL}:{MQTT_BROKER_PORT}")
        client.subscribe(MQTT_SUB_TOPIC)
        print(f"MQTT: Suscrito al tópico '{MQTT_SUB_TOPIC}'")
        # Emitir un mensaje a la UI si está conectada
        socketio.emit("server_message", {"type": "info", "text": "MQTT client connected."}, namespace="/")
    else:
        print(f"MQTT: Fallo al conectar, código de retorno: {rc}")
        socketio.emit("server_message", {"type": "error", "text": f"MQTT connection failed (code {rc})."}, namespace="/")

def on_message(client, userdata, msg):
    """Callback que se ejecuta cuando se recibe un mensaje MQTT."""
    print(f"MQTT: Mensaje recibido en '{msg.topic}': {msg.payload.decode()}")
    try:
        data = json.loads(msg.payload.decode())

        # Validar la estructura del payload MQTT, similar al endpoint HTTP
        if not all(k in data for k in ("device", "sensors")):
            print("MQTT Error: Missing required sensor data fields (device, sensors) in payload.")
            socketio.emit("server_message", {"type": "error", "text": "MQTT payload invalid: missing device/sensors."}, namespace="/")
            return

        device = data["device"]
        sensors = data["sensors"]

        for sensor in sensors:
            if not all(k in sensor for k in ("type", "value")):
                print("MQTT Error: Each sensor must have 'type' and 'value' fields.")
                socketio.emit("server_message", {"type": "error", "text": "MQTT sensor item invalid: missing type/value."}, namespace="/")
                return
            
            # Insertar los datos en la base de datos
            insert_sensor_data(device, sensor["type"], sensor["value"])

        # Emitir los datos a todos los clientes de Socket.IO conectados
        socketio.emit("sensor_update", data, namespace="/")

    except json.JSONDecodeError:
        print(f"MQTT Error: Could not decode JSON from message: {msg.payload.decode()}")
        socketio.emit("server_message", {"type": "error", "text": "MQTT payload not valid JSON."}, namespace="/")
    except Exception as e:
        print(f"MQTT Error processing message: {e}")
        socketio.emit("server_message", {"type": "error", "text": f"MQTT message processing error: {e}"}, namespace="/")

# --- Configuración y Conexión MQTT ---

def setup_mqtt_client():
    global mqtt_client
    try:
        mqtt_client = mqtt.Client(client_id="flask_server_app") # ID único para el cliente
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        mqtt_client.connect_async(MQTT_BROKER_URL, MQTT_BROKER_PORT, 60) # Conexión asíncrona
        mqtt_client.loop_start() # Inicia el hilo de bucle en segundo plano
        print(f"MQTT: Trying to connect to Broker with path {MQTT_BROKER_URL}:{MQTT_BROKER_PORT}...")
    except Exception as e:
        print(f"MQTT Error:Can not config or connect MQTT client: {e}")
        socketio.emit("server_message", {"type": "error", "text": f"MQTT setup failed: {e}"}, namespace="/")
        mqtt_client = None 

# --- Rutas Flask ---

@app.route("/")
def index():
    """Sirve el dashboard web."""
    return render_template("index.html")

# --- Socket.IO Event Handlers ---

@socketio.on("connect")
def on_connect_socketio():
    """Se ejecuta cuando un cliente de Socket.IO se conecta."""
    print("Socket.IO: Cliente conectado.")
    state = get_led_state() # Obtener el estado actual de los LEDs de la DB
    emit("led_update", state) 

@socketio.on("control_led")
def on_control_led(data):
    """
    Recibe comandos de control de LED desde el dashboard y los envía al ESP32
    y al broker MQTT.
    """
    update_led_state(data)
    
    # 1. Enviar comando al ESP32 vía HTTP (alternativa si MQTT no está listo)
    try:
        requests.post(f"{ESP32_IP}/api/control-led", json=data)
        print(f"HTTP: Enviado control de LED a ESP32 ({ESP32_IP}): {data}")
    except Exception as e:
        print(f"HTTP: Fallo al contactar al ESP32 ({ESP32_IP}): {e}")
        # Emitir error al frontend si la conexión HTTP falla
        emit("server_message", {"type": "error", "text": f"Failed to control ESP32 via HTTP: {e}"}, namespace="/")

    # 2. Publicar comando en MQTT (opción preferida si MQTT está configurado)
    if mqtt_client and mqtt_client.is_connected():
        try:
            # Puedes enviar un payload más específico si el ESP32 lo espera así
            # Por ejemplo, {"red": 1} o {"command": "toggle_red_led"}
            mqtt_payload = {
                "ledRed": data.get("ledRed"),
                "ledGreen": data.get("ledGreen")
            }
            mqtt_client.publish(MQTT_PUB_TOPIC, json.dumps(mqtt_payload))
            print(f"MQTT: Publicado comando de LED en '{MQTT_PUB_TOPIC}': {mqtt_payload}")
        except Exception as e:
            print(f"MQTT: Failed to publish command via MQTT: {e}")
            emit("server_message", {"type": "error", "text": f"Failed to publish LED command via MQTT: {e}"}, namespace="/")
    else:
        print("MQTT: MQTT client not connected, could not publish LED command.")
        emit("server_message", {"type": "info", "text": "MQTT not connected, LED command sent via HTTP only."}, namespace="/")


    # Emitir el estado actualizado de los LEDs a todos los clientes de Socket.IO
    emit("led_update", data, broadcast=True)

# --- HTTP Endpoint para recibir datos de sensores (Alternativa/Respaldo) ---

@app.route("/api/sensor", methods=["POST"])
def update_sensor_data_http():
    """
    Endpoint HTTP para que los microcontroladores envíen datos de sensores.
    Esto sirve como respaldo si la publicación MQTT falla o no se usa en el ESP32.
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
            insert_sensor_data(device, sensor["type"], sensor["value"])

        # Emitir los datos a todos los clientes de Socket.IO conectados
        socketio.emit("sensor_update", data, namespace="/")
        return jsonify({"status": "success", "message": "Sensor data received and processed."}), 200
    except Exception as e:
        print(f"Error processing sensor data via HTTP: {e}")
        return jsonify({"status": "error", "message": f"Error processing sensor data via HTTP: {e}"}), 500

# --- Inicio de la Aplicación ---

if __name__ == "__main__":
    init_db() 
    setup_mqtt_client() # Configurar y conectar el cliente MQTT

    # Iniciar el servidor Flask-SocketIO
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)

    # Cuando el servidor se detenga, detener el bucle de MQTT
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("MQTT: Cliente MQTT desconectado.")
