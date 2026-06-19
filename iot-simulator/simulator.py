import paho.mqtt.client as mqtt
import json
import time
import random
import os

BROKER = os.environ.get("MQTT_BROKER", "localhost")
PORT = int(os.environ.get("MQTT_PORT", "1883"))
TOPIC = "futurekawa/bresil/mesures"
INTERVAL = 10  # Publication toutes les 10 secondes

# Configurations cibles de chaque module pour simuler des données cohérentes
MODULES_CONFIG = {
    "br-santos-01": {
        "temp_ideale": 29.0,
        "tolerance_temp": 3.0, # Plage nominale: 26.0 - 32.0
        "hum_ideale": 55.0,
        "tolerance_hum": 2.0   # Plage nominale: 53.0% - 57.0%
    },
    "br-rio-02": {
        "temp_ideale": 29.0,
        "tolerance_temp": 3.0, # Plage nominale: 26.0 - 32.0
        "hum_ideale": 55.0,
        "tolerance_hum": 2.0   # Plage nominale: 53.0% - 57.0%
    },
    "col-medellin-01": {
        "temp_ideale": 26.0,
        "tolerance_temp": 3.0, # Plage nominale: 23.0 - 29.0
        "hum_ideale": 80.0,
        "tolerance_hum": 2.0   # Plage nominale: 78.0% - 82.0%
    }
}

def generate_payload():
    # Sélectionner un module aléatoire parmi les modules actifs
    module_id = random.choice(list(MODULES_CONFIG.keys()))
    cfg = MODULES_CONFIG[module_id]

    # 15% de chances de générer une anomalie (hors tolérance)
    is_anomaly = random.random() < 0.00

    if is_anomaly:
        # Générer une valeur hors tolérance
        if random.choice([True, False]):
            # Anomalie de température (trop haute ou trop basse)
            temp = round(cfg["temp_ideale"] + random.choice([1, -1]) * (cfg["tolerance_temp"] + random.uniform(0.5, 4.0)), 2)
            humid = round(cfg["hum_ideale"] + random.uniform(-cfg["tolerance_hum"] + 0.1, cfg["tolerance_hum"] - 0.1), 2)
        else:
            # Anomalie d'humidité (trop haute ou trop basse)
            temp = round(cfg["temp_ideale"] + random.uniform(-cfg["tolerance_temp"] + 0.1, cfg["tolerance_temp"] - 0.1), 2)
            humid = round(cfg["hum_ideale"] + random.choice([1, -1]) * (cfg["tolerance_hum"] + random.uniform(0.5, 5.0)), 2)
        status = "ALERT"
    else:
        # Valeurs conformes aux cibles
        temp = round(cfg["temp_ideale"] + random.uniform(-cfg["tolerance_temp"] + 0.3, cfg["tolerance_temp"] - 0.3), 2)
        humid = round(cfg["hum_ideale"] + random.uniform(-cfg["tolerance_hum"] + 0.3, cfg["tolerance_hum"] - 0.3), 2)
        status = "nominal"

    return {
        "temperature": temp,
        "humidite": humid,
        "id_module": module_id
    }, status

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"Simulateur connecté au broker {BROKER}:{PORT}")
        print(f"Publication sur : {TOPIC} toutes les {INTERVAL}s\n")
    else:
        print(f"Echec de connexion au broker, code : {rc}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.connect(BROKER, PORT, 60)
client.loop_start()

print("Simulateur IoT FutureKawa démarré...")
try:
    while True:
        payload, status = generate_payload()

        client.publish(TOPIC, json.dumps(payload))
        print(f"[{status.upper()}] Temp: {payload['temperature']}°C | "
              f"Humidite: {payload['humidite']}% | "
              f"Module: {payload['id_module']}")

        time.sleep(INTERVAL)
except KeyboardInterrupt:
    print("\nSimulateur arrêté.")
    client.loop_stop()
    client.disconnect()