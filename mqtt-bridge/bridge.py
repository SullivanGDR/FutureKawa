import paho.mqtt.client as mqtt
import json
import urllib.request
from datetime import datetime

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "futurekawa/bresil/mesures"
API_URL = "http://localhost:8000/api/v1/releves/"

def forward_to_api(payload):
    """Transmet le relevé IoT au serveur FastAPI."""
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        # Envoi de la requête POST synchrone
        with urllib.request.urlopen(req) as response:
            status_code = response.status
            if status_code in (200, 201):
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Transmis a l'API : {payload}")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Erreur API (Code: {status_code})")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Impossible de joindre l'API : {e}")

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Bridge MQTT connecte au broker {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
        print(f"Transmission : MQTT ({MQTT_TOPIC}) ---> FastAPI ({API_URL})\n")
    else:
        print(f"Echec de connexion au broker MQTT, code : {rc}")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        forward_to_api(data)
    except Exception as e:
        print(f"Erreur de traitement du payload MQTT : {e}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

print("Bridge MQTT -> FastAPI demarre...")
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nBridge MQTT arrete.")
    client.disconnect()