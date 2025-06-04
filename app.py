from flask import Flask, render_template, request, redirect, url_for
from db import collection, get_all_data
from mqtt_handler import latest_data, start_mqtt_loop
import plotly.graph_objs as go
from plotly.offline import plot
import threading

app = Flask(__name__)

def create_and_save_plot(values, label, filename, pump_lines):
    trace = go.Scatter(x=list(range(len(values))), y=values, mode="lines+markers",
                       name=label, line=dict(color="blue"))

    pump_markers = [
        go.Scatter(x=[i, i], y=[0, max(values) if values else 1], mode='lines',
                   line=dict(color='red'), name='Pump ON', showlegend=False)
        for i in pump_lines
    ]

    fig = go.Figure([trace] + pump_markers)
    fig.update_layout(title=label)
    fig.write_html(f"static/{filename}", include_plotlyjs="cdn")

@app.route("/")
def index():
    data = get_all_data()

    soil = [d["soil"] for d in data]
    water = [d["water"] for d in data]
    pump_lines = [i for i, d in enumerate(data) if d.get("pump")]

    latest_soil = soil[0] if soil else "N/A"
    latest_water = water[0] if water else "N/A"

    create_and_save_plot(soil, "Soil Moisture", "soil_plot.html", pump_lines)
    create_and_save_plot(water, "Water Level", "water_plot.html", pump_lines)

    watered = request.args.get("watered") == "yes"

    return render_template("index.html",
                           data=data,
                           latest_soil=latest_soil,
                           latest_water=latest_water,
                           watered=watered)

@app.route("/water", methods=["POST"])
def water_plants():
    import paho.mqtt.client as mqtt

    client = mqtt.Client()
    client.tls_set()
    client.username_pw_set("client1", "Password1")
    client.connect("5d8958dd403d415196e6c9e009168278.s1.eu.hivemq.cloud", 8883, 60)
    result = client.publish("smartfarm/pump_command", "on")
    print("📡 Publish result:", result.rc)
    client.disconnect()

    return redirect(url_for("index", watered="yes"))

# Start background MQTT thread on app start
threading.Thread(target=start_mqtt_loop, daemon=True).start()