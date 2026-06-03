import serial
import json
from datetime import datetime
import os
import re
import time

SERIAL_PORT = 'COM7'
BAUD_RATE = 9600
OUTPUT_FILE = 'C:/xampp/htdocs/smart-lab/co2_log.json'

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

print(f"Connecting to Arduino on {SERIAL_PORT}...")
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=3)
    time.sleep(2)
    print("Database sync engine online. Monitoring hardware stream...\n")

    staged_rfid = "None"

    while True:
        raw_bytes = ser.readline()
        if not raw_bytes:
            continue

        line = raw_bytes.decode('utf-8', errors='replace').strip()
        if not line:
            continue

        print(f"🔍 [SERIAL IN]: {line}")

        # 1. CAPTURE RFID
        if "UID:" in line or "Tag Detected" in line:
            match = re.search(r'UID:\s*([0-9A-Fa-f\s]+)', line, re.IGNORECASE)
            if match:
                staged_rfid = match.group(1).replace(" ", "").strip().upper()
                print(f"   🪪 STAGED CARD: {staged_rfid}")
            continue

        # 2. CAPTURE CO2 — matches "CO2:847PPM" or "CO2: 847 PPM"
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
            log_entry = {
                "date": now.strftime("%Y-%m-%d"),
                "timestamp": now.strftime("%H:%M:%S"),
                "co2_ppm": ppm,
                "status": status,
                "color": color,
                "bg": bg,
                "rfid_tag": staged_rfid
            }

            try:
                logs = []
                if os.path.exists(OUTPUT_FILE):
                    with open(OUTPUT_FILE, 'r') as f:
                        try:
                            logs = json.load(f)
                            if not isinstance(logs, list):
                                logs = []
                        except json.JSONDecodeError:
                            logs = []

                logs.append(log_entry)
                if len(logs) > 100:
                    logs = logs[-100:]

                with open(OUTPUT_FILE, 'w') as f:
                    json.dump(logs, f, indent=4)

                print(f"   💾 LOGGED | CO2: {ppm} PPM | Status: {status} | RFID: {staged_rfid}")

            except Exception as write_error:
                print(f"   ❌ WRITE FAILURE: {write_error}")

            staged_rfid = "None"

except KeyboardInterrupt:
    print("\nLogging stopped cleanly.")
except Exception as e:
    print(f"\nCritical connection error: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()