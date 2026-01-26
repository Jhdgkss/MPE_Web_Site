import requests
import time
import random
import json

# CONFIGURATION
SERVER_URL = "http://127.0.0.1:8000/api/ingest/"
MACHINE_ID = "i6" # Change to 'i3' or 'test' as needed

def generate_sensor_data():
    """
    Simulates reading values from a PLC or Sensor.
    Replace this logic with actual Modbus/OPC-UA reads later.
    """
    # Simulate a running machine with slight fluctuations
    target_ppm = 30.0
    target_temp = 175.0
    
    current_ppm = round(target_ppm + random.uniform(-1.5, 1.5), 1)
    current_temp = round(target_temp + random.uniform(-0.5, 0.5), 1)
    
    # Determine status based on random chance
    status = "RUNNING"
    if random.random() > 0.95:
        status = "STOPPED"
        current_ppm = 0
        
    return {
        "machine_id": MACHINE_ID,
        "ppm": current_ppm,
        "temp": current_temp,
        "batch_count": int(time.time()) % 10000, # Fake growing batch
        "status": status
    }

def main():
    print(f"--- Starting Telemetry Client for {MACHINE_ID} ---")
    print(f"Target: {SERVER_URL}")
    
    while True:
        # 1. Read Sensors
        payload = generate_sensor_data()
        
        # 2. Send to Django
        try:
            response = requests.post(SERVER_URL, json=payload)
            
            if response.status_code == 200:
                print(f"[OK] Sent: {payload['ppm']}ppm | {payload['temp']}C")
            else:
                print(f"[ERROR] Server returned {response.status_code}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("[ERROR] Could not connect to server. Is Django running?")
            
        # 3. Wait before next update
        time.sleep(1.0) # Send every 1 second

if __name__ == "__main__":
    main()