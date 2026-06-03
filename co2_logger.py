import serial
import json
from datetime import datetime
import os
import re
import time

SERIAL_PORT = 'COM7'
BAUD_RATE = 9600
CO2_FILE = 'C:/xampp/htdocs/smart-lab/co2_log.json'

os.makedirs(os.path.dirname(CO2_FILE), exist_ok=True)

print("CO2 Logger starting on COM7...")
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=3)
    time.sleep(2)
    print("CO2 stream active. Logging continuously...\n")

    while True:
        raw = ser.readline()
        if not raw:
            continue
        line = raw.decode('utf-8', errors='replace').strip()
        if not line:
            continue

        print(f"[IN]: {line}")

        co2_match = re.search(r'CO2\s*[:\s]\s*(\d+)\s*PPM', line, re.IGNORECASE)
        if co2_match:
            ppm = int(co2_match.group(1))

            if ppm <= 600:
                status, color, bg = "Excellent", "#2E8B57", "#EAF4EF"
            elif ppm <= 1000:
                status, color, bg = "Good", "#1E6FBA", "#E8F0F8"
            elif ppm <= 1500:
                status, color, bg = "Fair (Stale)", "#D4AF37", "#FAF6E8"
            else:
                status, color, bg = "Poor / Vent Required", "#DC3545", "#FDF2F3"

            now = datetime.now()
            entry = {
                "date": now.strftime("%Y-%m-%d"),
                "timestamp": now.strftime("%H:%M:%S"),
                "co2_ppm": ppm,
                "status": status,
                "color": color,
                "bg": bg
            }

            try:
                logs = []
                if os.path.exists(CO2_FILE):
                    with open(CO2_FILE, 'r') as f:
                        try:
                            logs = json.load(f)
                            if not isinstance(logs, list): logs = []
                        except json.JSONDecodeError:
                            logs = []
                logs.append(entry)
                if len(logs) > 500: logs = logs[-500:]
                with open(CO2_FILE, 'w') as f:
                    json.dump(logs, f, indent=4)
                print(f"   💾 CO2 LOGGED: {ppm} PPM | {status}")
            except Exception as e:
                print(f"   ❌ Write error: {e}")

except KeyboardInterrupt:
    print("\nCO2 logger stopped.")
except Exception as e:
    print(f"\nError: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()