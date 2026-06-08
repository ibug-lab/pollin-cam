import time
import board
import adafruit_dht
import csv
from datetime import datetime

# --- Setup DHT22 on GPIO4 ---
# Adjust as needed for whichever GPIO pin is used (be sure to enable w1 in raspiconfig)
dht_device = adafruit_dht.DHT22(board.D27)

# --- CSV file name ---
csv_file = "/media/pollincam-01/ambient-temps.csv"

# --- Create CSV file with header if it doesn't exist ---
try:
    with open(csv_file, "x", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "temperature_C", "humidity_percent"])
except FileExistsError:
    pass  # File already exists

print("Starting DHT22 logging... Press Ctrl+C to stop.")

while True:
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity

        if temperature is not None and humidity is not None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"{timestamp} | Temp: {temperature:.1f} C | Humidity: {humidity:.1f}%")

            with open(csv_file, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, temperature, humidity])

        else:
            print("Sensor returned None. Retrying...")

    except RuntimeError as error:
        # DHT sensors often throw runtime errors — safe to ignore and retry
        print(f"Reading error: {error}")
    
    except Exception as error:
        print(f"Unexpected error: {error}")
        dht_device.exit()
        break

    time.sleep(60)  # Read every 60 seconds
