#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

const char* ssid = "Wokwi-GUEST";
const char* password = "";

const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_topic = "futurekawa/bresil/mesures";

#define DHTPIN 15
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

const char* id_module = "br-santos-01";

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastPublish = 0;
const unsigned long INTERVAL = 120;

void setupWiFi() {
  Serial.print("Connexion au WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connecte, IP: " + WiFi.localIP().toString());
}

void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("Connexion MQTT...");
    String clientId = "ESP32-" + String(id_module);
    if (client.connect(clientId.c_str())) {
      Serial.println(" connecte !");
    } else {
      Serial.print(" echec, rc=");
      Serial.print(client.state());
      Serial.println(" -> nouvelle tentative dans 2s");
      delay(2000);
    }
  }
}

void publishMeasure() {
  float humidite = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidite) || isnan(temperature)) {
    Serial.println("Erreur de lecture DHT22, on saute ce cycle");
    return;
  }

  char payload[200];
  snprintf(payload, sizeof(payload),
    "{\"temperature\": %.2f, \"humidite\": %.2f, \"id_module\": \"%s\"}",
    temperature, humidite, id_module);

  client.publish(mqtt_topic, payload);

  Serial.print("Publie -> ");
  Serial.println(payload);
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  setupWiFi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnectMQTT();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastPublish > INTERVAL) {
    lastPublish = now;
    publishMeasure();
  }
}