import paho.mqtt.client as mqtt
import psycopg2
import json
import time
from datetime import datetime, timedelta

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "futurekawa/bresil/mesures"

DB_CONFIG = {
    "host": "localhost",
    "database": "MSPR_TPRE814_Bresil",
    "user": "postgres",
    "password": "root"
}

TEMP_IDEALE = 29.0
HUMID_IDEALE = 55.0
TOLERANCE_TEMP = 3.0
TOLERANCE_HUMID = 2.0
DELAI_PEREMPTION_JOURS = 365

def get_db_connection():
    while True:
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.autocommit = False
            print("✅ Connecté à PostgreSQL !")
            return conn
        except Exception as e:
            print(f"⏳ DB non disponible, retry dans 3s... ({e})")
            time.sleep(3)

def is_hors_tolerance(temperature, humidite):
    temp_ok = abs(temperature - TEMP_IDEALE) <= TOLERANCE_TEMP
    humid_ok = abs(humidite - HUMID_IDEALE) <= TOLERANCE_HUMID
    return not (temp_ok and humid_ok)

def verifier_et_mettre_a_jour_statuts(cursor, id_module):
    date_limite = datetime.now() - timedelta(days=DELAI_PEREMPTION_JOURS)

    cursor.execute("""
        UPDATE lot SET statut = 'perime'
        WHERE id_entrepot = (
            SELECT id_entrepot FROM module_iot WHERE id_module = %s
        )
        AND date_stockage < %s
        AND statut != 'perime'
    """, (id_module, date_limite))

    nb_perime = cursor.rowcount
    if nb_perime > 0:
        print(f"🗓️  {nb_perime} lot(s) marqué(s) comme périmé(s)")

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"✅ Bridge connecté au broker {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
        print(f"👂 Écoute sur : {MQTT_TOPIC}\n")
    else:
        print(f"❌ Échec connexion broker, code : {rc}")

def on_message(client, userdata, msg):
    conn = userdata["conn"]
    cursor = userdata["cursor"]

    try:
        data = json.loads(msg.payload.decode())
        temp = data["temperature"]
        humid = data["humidite"]
        id_module = data["id_module"]

        hors_tol = is_hors_tolerance(temp, humid)
        statut_label = "⚠️  HORS TOLÉRANCE" if hors_tol else "✅ nominal"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] "
              f"Temp: {temp}°C | Humidité: {humid}% | {statut_label}")

        cursor.execute("""
            INSERT INTO releve_mesure (temperature, humidite, id_module)
            VALUES (%s, %s, %s)
        """, (temp, humid, id_module))

        if hors_tol:
            cursor.execute("""
                UPDATE lot SET statut = 'alerte'
                WHERE id_entrepot = (
                    SELECT id_entrepot FROM module_iot WHERE id_module = %s
                )  
                AND statut = 'conforme'
            """, (id_module,))
            nb = cursor.rowcount
            if nb > 0:
                print(f"   ↳ {nb} lot(s) passé(s) en alerte")

        verifier_et_mettre_a_jour_statuts(cursor, id_module)

        conn.commit()
        print(f"   ↳ Enregistré en base.\n")

    except KeyError as e:
        conn.rollback()
        print(f"❌ Champ manquant dans le payload : {e}")
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur : {e}")

conn = get_db_connection()
cursor = conn.cursor()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.user_data_set({"conn": conn, "cursor": cursor})
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)

print("Bridge MQTT → PostgreSQL démarré...")
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nBridge arrêté.")
    cursor.close()
    conn.close()
    client.disconnect()