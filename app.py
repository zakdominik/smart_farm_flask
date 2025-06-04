from flask import Flask, render_template, redirect, url_for, flash, get_flashed_messages
import paho.mqtt.client as mqtt
from pymongo import MongoClient
import json
import threading
from plotly.offline import plot
import plotly.graph_objs as go
import time

app = Flask(__name__)
app.secret_key = "smartfarm-secret-key"

# MongoDB connection
mongo_client = MongoClient("mongodb+srv://farmuser:farm12345@cluster88013.uygbstv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster88013")
db = mongo_client.smartfarm
collection = db.readings

# MQTT settings
MQTT_BROKER = "5d8958dd403d415196e6c9e009168278.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "client1"
MQTT_PASS = "Password1"
MQTT_TOPIC_DATA = "smartfarm/data"
MQTT_TOPIC_PUMP = "smartfarm/pump"
MQTT_TOPIC_COMMAND = "smartfarm/pump_command"

def on_connect(client, userdata, flags, rc):
    client.subscribe([(MQTT_TOPIC_DATA, 0), (MQTT_TOPIC_PUMP, 0)])

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        if msg.topic == MQTT_TOPIC_DATA:
            data = json.loads(payload)
            collection.insert_one(data)
        elif msg.topic == MQTT_TOPIC_PUMP:
            # Optional: log pump events if needed
            pass
    except Exception as e:
        print("Error handling message:", e)

def mqtt_loop():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.tls_set()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

@app.route("/")
def index():
    data = list(collection.find({}, {"_id": 0}))
    data.reverse()

    labels = list(range(len(data)))
    soil = [d["soil"] for d in data]
    water = [d["water"] for d in data]
    pump_lines = [i for i, d in enumerate(data) if d.get("pump")]

    latest_soil = soil[0] if soil else "N/A"
    latest_water = water[0] if water else "N/A"

    def create_plot(values, label):
        trace = go.Scatter(x=labels, y=values, mode="lines+markers", name=label, line=dict(color="blue"))
        pump_markers = [
            go.Scatter(x=[i, i], y=[0, max(values)], mode='lines', line=dict(color='red'), name='Pump ON', showlegend=False)
            for i in pump_lines
        ]
        return plot([trace] + pump_markers, output_type="div", include_plotlyjs=False)

    soil_plot = create_plot(soil, "Soil Moisture")
    water_plot = create_plot(water, "Water Level")
    messages = get_flashed_messages()

    return render_template("index.html",
                           data=data,
                           latest_soil=latest_soil,
                           latest_water=latest_water,
                           soil_plot=soil_plot,
                           water_plot=water_plot,
                           messages=messages)

@app.route("/water", methods=["POST"])
def water_plants():
    client = mqtt.Client(client_id="flask-water-button")
    client.tls_set()
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    client.loop_start()  # Starts network loop in background

    result = client.publish(MQTT_TOPIC_COMMAND, "on")
    print("📡 Publish result:", result.rc)

    # 🔁 Wait to ensure message is sent
    time.sleep(1)

    client.loop_stop()
    client.disconnect()

    flash("Watering triggered.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    threading.Thread(target=mqtt_loop, daemon=True).start()
    app.run(debug=True)