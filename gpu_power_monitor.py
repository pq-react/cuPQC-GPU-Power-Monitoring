import time
import subprocess
import requests
import socket

# InfluxDB settings
INFLUXDB_URL = "http://<influxdb_IP_address>:8086/api/v2/write"
INFLUXDB_BUCKET = "<bucket_name>"
INFLUXDB_ORG = "<organization_name>"
INFLUXDB_TOKEN = "<influx_token>"

# Get the hostname of the machine
HOSTNAME = socket.gethostname()

# Headers for InfluxDB
HEADERS = {
    "Authorization": f"Token {INFLUXDB_TOKEN}",
    "Content-Type": "text/plain; charset=utf-8"
}

def get_gpu_power_draw():
    """Executes nvidia-smi command to get the GPU power draw."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=power.draw", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, check=True
        )
        return float(result.stdout.strip())  # Convert to float
    except subprocess.CalledProcessError as e:
        print(f"Error executing nvidia-smi: {e}")
        return None
    except ValueError:
        print("Failed to parse GPU power draw.")
        return None

def send_to_influxdb(power_draw):
    """Formats and sends GPU power draw data to InfluxDB."""
    if power_draw is None:
        print("Skipping InfluxDB update due to missing power draw data.")
        return

    timestamp = int(time.time() * 1e9)  # Convert current time to nanoseconds
    data = f"gpu_metrics,host={HOSTNAME} power_draw={power_draw} {timestamp}"

    try:
        response = requests.post(
            f"{INFLUXDB_URL}?org={INFLUXDB_ORG}&bucket={INFLUXDB_BUCKET}&precision=ns",
            headers=HEADERS,
            data=data
        )
        if response.status_code == 204:
            print(f"✅ Data sent to InfluxDB: power_draw={power_draw}W")
        else:
            print(f"❌ Failed to send data to InfluxDB: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to InfluxDB: {e}")

if __name__ == "__main__":
    print("Starting GPU Power Monitoring...")
    while True:
        power_draw = get_gpu_power_draw()
        send_to_influxdb(power_draw)
        time.sleep(1)  # Wait 1 second before next measurement
