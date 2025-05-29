import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../automation.db")

def get_connection():
    """
    Establece una conexión a la base de datos SQLite.
    check_same_thread=False es necesario para el uso con Flask-SocketIO y Eventlet.
    """
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database at {DB_PATH}: {e}")
        return None

def init_db():
    """
    Inicializa la base de datos, creando las tablas necesarias si no existen.
    También inserta el estado inicial de los LEDs si la tabla está vacía.
    """
    with get_connection() as conn:
        if conn is None:
            print("Failed to get database connection during initialization.")
            return

        c = conn.cursor()
        try:
            # Tabla led_state
            c.execute("""
                CREATE TABLE IF NOT EXISTS led_state (
                    id INTEGER PRIMARY KEY,
                    red INTEGER DEFAULT 0,
                    green INTEGER DEFAULT 0
                )
            """)
            c.execute("INSERT OR IGNORE INTO led_state (id, red, green) VALUES (1, 0, 0)")
            conn.commit()
            print("Table 'led_state' checked/created and initialized.")
        except sqlite3.Error as e:
            print(f"Error creating/initializing 'led_state' table: {e}")

        # Crear otras tablas
        create_sensor_table(conn)
        create_devices_table(conn) # Función para crear la tabla de dispositivos

def create_sensor_table(conn):
    """
    Crea la tabla 'sensor_data' si no existe y añade un índice para optimización.
    """
    c = conn.cursor()
    try:
        c.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_name TEXT NOT NULL,
                sensor_type TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Añadir índice para optimizar consultas de datos de sensores
        c.execute("""
            CREATE INDEX IF NOT EXISTS idx_sensor_data_type_timestamp
            ON sensor_data (sensor_type, timestamp DESC);
        """)
        conn.commit()
        print("Table 'sensor_data' checked/created and indexed.")
    except sqlite3.Error as e:
        print(f"Error creating 'sensor_data' table or index: {e}")

def create_devices_table(conn):
    """
    Crea la tabla 'devices' para registrar los microcontroladores.
    """
    c = conn.cursor()
    try:
        c.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                ip TEXT NOT NULL,
                type TEXT NOT NULL,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Table 'devices' checked/created.")
    except sqlite3.Error as e:
        print(f"Error creating 'devices' table: {e}")


def insert_sensor_data(device_name, sensor_type, value):
    """
    Inserta un nuevo registro de datos de sensor en la tabla 'sensor_data'.
    """
    with get_connection() as conn:
        if conn is None: return
        c = conn.cursor()
        try:
            c.execute("""
                INSERT INTO sensor_data (device_name, sensor_type, value)
                VALUES (?, ?, ?)
            """, (device_name, sensor_type, value))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting sensor data for {device_name} ({sensor_type}, {value}): {e}")

def get_latest_sensor_data(sensor_type, limit=5):
    """
    Obtiene los últimos datos de un tipo de sensor específico.
    """
    with get_connection() as conn:
        if conn is None: return []
        c = conn.cursor()
        try:
            c.execute("""
                SELECT device_name, value, timestamp FROM sensor_data
                WHERE sensor_type = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (sensor_type, limit))
            return c.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting latest sensor data for {sensor_type}: {e}")
            return []

def get_all_sensor_data():
    """
    Obtiene todos los datos de sensores, ordenados por marca de tiempo.
    """
    with get_connection() as conn:
        if conn is None: return []
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC")
            return c.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting all sensor data: {e}")
            return []

def get_led_state():
    """
    Obtiene el estado actual de los LEDs.
    """
    with get_connection() as conn:
        if conn is None: return {"ledRed": 0, "ledGreen": 0} # Retornar estado por defecto en caso de error
        c = conn.cursor()
        try:
            c.execute("SELECT red, green FROM led_state WHERE id = 1")
            row = c.fetchone()
            if row:
                return {"ledRed": row[0], "ledGreen": row[1]}
            else:
                # Si por alguna razón no hay fila, intentar inicializarla o retornar default
                print("LED state not found, re-initializing.")
                init_db() # Re-inicializar para asegurar que la fila exista
                return {"ledRed": 0, "ledGreen": 0}
        except sqlite3.Error as e:
            print(f"Error getting LED state: {e}")
            return {"ledRed": 0, "ledGreen": 0} # Retornar estado por defecto en caso de error

def update_led_state(new_state):
    """
    Actualiza el estado de los LEDs en la base de datos.
    """
    with get_connection() as conn:
        if conn is None: return
        c = conn.cursor()
        try:
            c.execute("""
                UPDATE led_state
                SET red = ?, green = ?
                WHERE id = 1
            """, (new_state["ledRed"], new_state["ledGreen"]))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error updating LED state to {new_state}: {e}")

def register_device(name, ip, device_type):
    """
    Registra o actualiza un dispositivo en la tabla 'devices'.
    Utiliza INSERT OR REPLACE para actualizar si el dispositivo ya existe por nombre.
    """
    with get_connection() as conn:
        if conn is None: return
        c = conn.cursor()
        try:
            c.execute("""
                INSERT OR REPLACE INTO devices (name, ip, type, last_seen)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (name, ip, device_type))
            conn.commit()
            print(f"Device '{name}' registered/updated with IP '{ip}' and type '{device_type}'.")
        except sqlite3.Error as e:
            print(f"Error registering/updating device '{name}': {e}")

def get_all_devices():
    """
    Obtiene todos los dispositivos registrados.
    """
    with get_connection() as conn:
        if conn is None: return []
        c = conn.cursor()
        try:
            c.execute("SELECT name, ip, type, last_seen FROM devices ORDER BY last_seen DESC")
            return c.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting all devices: {e}")
            return []
