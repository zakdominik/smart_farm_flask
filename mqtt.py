import json
import threading
import paho.mqtt.client as mqtt
from db import collection

#HiveMQ Cloud connection information
mqtt_broker_connection = "5d8958dd403d415196e6c9e009168278.s1.eu.hivemq.cloud"
port = 8883
mqtt_user = "client1"
mqtt_password = "Password1"
mqtt_sensor_readings = "smartfarm/data"
mqtt_pump_readings = "smartfarm/pump"

#dictionary where the latest data will be stored
latest_data = {"soil": "N/A", "water": "N/A", "pump": "off"}

#connects to MQTT broker, in this case HiveMQ
def on_connect(client, userdata, flags, rc):
    client.subscribe([(mqtt_sensor_readings, 0), (mqtt_pump_readings, 0)])

#reads and stores the latest readings to MongoDB
def on_message(client, userdata, msg):
    global latest_data
    payload = msg.payload.decode()
    if msg.topic == mqtt_sensor_readings:
        try:
            data = json.loads(payload)
            latest_data.update(data)
            collection.insert_one(data)
        except Exception as e:
            print(f"Error decoding MQTT payload: {e}")
    elif msg.topic == mqtt_pump_readings:
        latest_data["pump"] = payload

#keeps the mqtt connection live at all times
def start_mqtt_loop():
    client = mqtt.Client()
    client.username_pw_set(mqtt_user, mqtt_password)
    client.tls_set()  # Use default system certs
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_broker_connection, port, 60)
    client.loop_forever()

#creates a new thread so that the Flask app and the MQTT connection can both run at the same time
def start_background_tasks():
    thread = threading.Thread(target=start_mqtt_loop, daemon=True)
    thread.start()