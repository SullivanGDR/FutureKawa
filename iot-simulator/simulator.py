import paho.mqtt.client as mqtt
import json
import time
import random

BROKER = "localhost"
PORT = 1883
TOPIC = "futurekawa/bresil/mesures"
INTERVAL = 10

TARGET_TEMP = 29.0
TARGET_HUMID = 55.0

def generate_payload():
    temp = round(TARGET_TEMP + random.uniform(-2, 2), 2)
    humid = round(TARGET_HUMID + random.uniform(-1.5, 1.5), 2)

    return {
        "temperature": temp,
        "humidite": humid,
        "id_module": "MAC-BRESIL-01"
    }

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"✅ Simulateur connecté au broker {BROKER}:{PORT}")
        print(f"📡 Publication sur : {TOPIC} toutes les {INTERVAL}s\n")
    else:
        print(f"❌ Échec de connexion, code : {rc}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.connect(BROKER, PORT, 60)
client.loop_start()

try:
    while True:
        payload = generate_payload()

        client.publish(TOPIC, json.dumps(payload))
        print(f"[nominal] Temp: {payload['temperature']}°C | "
              f"Humidité: {payload['humidite']}% | "
              f"Module: {payload['id_module']}")

        time.sleep(INTERVAL)
except KeyboardInterrupt:
    print("\nSimulateur arrêté.")
    client.loop_stop()
    client.disconnect()