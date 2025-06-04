import json
import threading
import paho.mqtt.client as mqtt
from db import collection

# MQTT broker settings (HiveMQ Cloud)
MQTT_BROKER = "5d8958dd403d415196e6c9e009168278.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "client1"
MQTT_PASS = "Password1"
MQTT_TOPIC_DATA = "smartfarm/data"
MQTT_TOPIC_PUMP = "smartfarm/pump"

# Shared dictionary with latest values
latest_data = {"soil": "N/A", "water": "N/A", "pump": "off"}

def on_connect(client, userdata, flags, rc):
    client.subscribe([(MQTT_TOPIC_DATA, 0), (MQTT_TOPIC_PUMP, 0)])

def on_message(client, userdata, msg):
    global latest_data
    payload = msg.payload.decode()
    if msg.topic == MQTT_TOPIC_DATA:
        try:
            data = json.loads(payload)
            latest_data.update(data)
            collection.insert_one(data)
        except Exception as e:
            print(f"Error decoding MQTT payload: {e}")
    elif msg.topic == MQTT_TOPIC_PUMP:
        latest_data["pump"] = payload

def start_mqtt_loop():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.tls_set()  # Use default system certs
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()