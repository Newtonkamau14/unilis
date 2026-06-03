from http.server import HTTPServer, BaseHTTPRequestHandler
import serial
import json
import re
import time
import os
from datetime import datetime

SERIAL_PORT = 'COM7'   # <-- Use a DIFFERENT COM port or virtual port splitter
BAUD_RATE = 9600
CARDS_FILE = 'C:/xampp/htdocs/smart-lab/cards_log.json'
PORT = 8765

os.makedirs(os.path.dirname(CARDS_FILE), exist_ok=True)

# Shared serial connection
ser = None

def get_serial():
    global ser
    if ser is None or not ser.is_open:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=12)
        time.sleep(2)
    return ser

class RFIDHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress default HTTP logs

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.end_headers()

    def do_GET(self):
        if self.path == '/scan':
            try:
                s = get_serial()
                s.write(b'SCAN\n')
                print("📡 SCAN command sent. Waiting for card...")

                uid = None
                deadline = time.time() + 12
                while time.time() < deadline:
                    raw = s.readline()
                    if not raw:
                        continue
                    line = raw.decode('utf-8', errors='replace').strip()
                    print(f"   [IN]: {line}")

                    uid_match = re.search(r'UID:([0-9A-Fa-f]+)', line)
                    if uid_match:
                        uid = uid_match.group(1).upper()
                        if uid == "TIMEOUT":
                            uid = None
                        break

                if uid:
                    now = datetime.now()
                    entry = {
                        "date": now.strftime("%Y-%m-%d"),
                        "timestamp": now.strftime("%H:%M:%S"),
                        "rfid_tag": uid
                    }
                    # Save to cards log
                    logs = []
                    if os.path.exists(CARDS_FILE):
                        with open(CARDS_FILE, 'r') as f:
                            try:
                                logs = json.load(f)
                                if not isinstance(logs, list): logs = []
                            except: logs = []
                    logs.append(entry)
                    with open(CARDS_FILE, 'w') as f:
                        json.dump(logs, f, indent=4)

                    print(f"   🪪 CARD SAVED: {uid}")
                    result = {"success": True, "uid": uid, "timestamp": entry["timestamp"]}
                else:
                    result = {"success": False, "error": "No card detected within timeout"}

            except Exception as e:
                result = {"success": False, "error": str(e)}

            body = json.dumps(result).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

print(f"RFID HTTP Server running on http://localhost:{PORT}")
print("Dashboard can now call http://localhost:8765/scan")
HTTPServer(('0.0.0.0', PORT), RFIDHandler).serve_forever()