# 🏠 Smart Home Automation - ESP32 + Flask + WebSockets + SQLite

Welcome to the cutting edge (or at least, the slightly less dull edge) of local smart home automation! This project is a Proof of Concept (PoC) for a delightful little system that blends microcontrollers, a backend server, and a slick web interface. Forget the cloud, your data's staying right here, under your digital roof.

## ✨ Key Features (Because who doesn't love features?)

-   **LED Control (ESP32):** Toggle LEDs on your ESP32 via HTTP or WebSocket. Because sometimes, you just need a light to turn on, without asking Alexa.
-   **Real-time Sensor Data Logging:** Temperature, humidity, light, sound... if it can sense it, we can log it! (Or at least, the ones we've hooked up so far.)
-   **Responsive Web Dashboard:** A sleek, minimalist web interface built with HTML/CSS and JavaScript, offering live updates. It looks good on your massive monitor, and surprisingly decent on your phone. No more scrolling endlessly through charts, thanks to our new graph selector!
-   **SQLite Database Storage:** All your precious sensor data is tucked away safely in a local SQLite database. Because who needs big data when you have *your* data?
-   **Flask + Socket.IO Backend:** A robust (and surprisingly fun) Python backend for real-time communication. It's like magic, but with more code.
-   **Flexible Server Deployment:** Designed to run comfortably on a Linux machine (like a Raspberry Pi or even a server on Termux on an Android phone, actually, this last one was our goal).
-   **Multi-sensor Support:** Reads data from ADS1115 (Light, Mic) and optionally from ESP32's internal ADCs. We're not picky; bring your own sensors!

## 🛠️ Technologies Used (The good stuff)

-   **Microcontroller:** ESP32 (formerly Raspberry Pi Pico in the PoC, but we've upgraded our brainpower!)
-   **Backend:** Python 3 + Flask + Flask-SocketIO
-   **Database:** SQLite (local, no cloud subscriptions required!)
-   **Frontend:** HTML, CSS (responsively redesigned with a cool palette), JavaScript (WebSockets, Chart.js)
-   **Server:** Any Linux-based system (including Android with Termux). Yes, your old phone can be a server, and yes, it's awesome.

## 📁 Project Structure (Because organization is key)

```
.
├── run.py                 # Main Flask server application (HTTP/WebSocket)
├── run-mqtt.py            # Alternative Flask server with MQTT integration
├── database.py            # SQLite database initialization and interaction
├── static/
│   ├── styles.css         # All the beautiful CSS for the dashboard (now cool and minimalist!)
│   └── logo.png           # Your brand new minimalist logo!
├── templates/
│   └── index.html         # The responsive web dashboard (now with graph selector!)
├── webenv/                # Python Virtual Environment (where all the magic libraries live)
├── start.sh               # Quick-start script for Linux/macOS
├── start.ps1              # Quick-start script for Windows PowerShell
├── start.cmd              # Quick-start script for Windows Command Prompt
├── requirements.txt       # List of Python dependencies (pip install -r this!)
├── README.md              # You are here!
└── LICENSE                # The MIT License (because sharing is caring)
```

## ⚙️ Installation & Setup (Let's get this party started!)

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/paul0pv/flaskHS.git](https://github.com/paul0pv/flaskHS.git)
    cd flaskHS
    ```

2.  **Create a Python Virtual Environment (Highly Recommended):**
    ```bash
    python3 -m venv webenv
    ```

3.  **Activate the Virtual Environment:**
    * **Linux/macOS:**
        ```bash
        source webenv/bin/activate
        ```
    * **Windows (PowerShell):**
        ```powershell
        .\webenv\Scripts\Activate.ps1
        ```
    * **Windows (Command Prompt):**
        ```cmd
        .\webenv\Scripts\activate.bat
        ```

4.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    (This might take a moment. Grab a coffee, or ponder the mysteries of the universe.)

5.  **Configure ESP32 (MicroPython):**
    * Update `boot.py` with your Wi-Fi SSID and password.
    * Update `main.py` (if not working with MQTT version) with your Flask server's IP address and port (e.g., `http://192.168.1.100:5000`).
    * Ensure functions/scripts for managing sensors and data (e.g., `data.py` and `devices.py`) are up-to-date on your microcontroller.

6.  **Start the Server:**
    * **Linux/macOS:**
        ```bash
        ./start.sh
        ```
    * **Windows (PowerShell):**
        ```powershell
        .\start.ps1
        ```
    * **Windows (Command Prompt):**
        ```cmd
        .\start.cmd
        ```
    (If everything goes well, you'll see some beautiful server logs, and the database will be initialized if it's the first run.)

## 🌐 Accessing the Dashboard (Your window to automation)

Open your favorite web browser and navigate to:

http://<YOUR-SERVER-IP>:5000/

(Replace `<YOUR-SERVER-IP>` with the actual IP address of the machine running your Flask server. Yes, the one you just set up.)

## 🧪 Sensor Data Endpoint (For the microcontrollers)

Microcontrollers can send their data via a `POST` request to:

POST /api/sensor
Content-Type: application/json


**Expected JSON Body:**
```json
{
  "device": "esp32_main",
  "sensors": [
    {
      "type": "light",
      "value": 1.23
    },
    {
      "type": "microphone",
      "value": 0.45
    }
  ]
}
```

(Yes, we accept multiple sensors in one go now! Efficiency is our middle name. Well, actually, it's probably "Automation".)

## 🤝 Contributing (Because two heads are better than one, especially when coding)
Got ideas? Found a bug? Just want to make things even more awesome? We welcome contributions! Feel free to fork this repository, make your changes, and submit a pull request. Let's build something cool together!

## 📜 License
This project is licensed under the MIT License. See the LICENSE file for details. You're free to use, modify, and distribute this code. Just give us a shout-out if you do something amazing with it!


