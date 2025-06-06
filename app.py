from flask import Flask, render_template, request, redirect, url_for
from db import get_all_data
from mqtt import *
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt

start_background_tasks() #enables Heroku to run both the mqtt connection and the app
app = Flask(__name__)

#function for creating line chart with points
def create_and_save_plot(values, label, filename):
    plt.figure(figsize=(8, 4))
    plt.plot(values[::-1], marker='o', label=label)
    plt.title(label)
    plt.xlabel("Count")
    plt.ylabel("Value")
    plt.tight_layout()
    plt.savefig(f"static/{filename}")
    plt.close()

#route for the main page, calls the plot functions, gets the data to be displayed, sends it to index.html
@app.route("/")
def index():

    data = get_all_data()

    soil = [d["soil"] for d in data]
    water = [d["water"] for d in data]
    latest_soil = soil[0] if soil else "N/A"
    latest_water = water[0] if water else "N/A"

    create_and_save_plot(soil, "Soil Moisture", "soil_plot.png")
    create_and_save_plot(water, "Water Level", "water_plot.png")

    watered = request.args.get("watered") == "yes"

    return render_template("index.html",
                           data=data,
                           latest_soil=latest_soil,
                           latest_water=latest_water,
                           watered=watered)

#route used for handling the Water Plants button. if the button is clicked then message on gets sent to mqtt
#the smart watering system receives this message and starts watering
@app.route("/water", methods=["POST"])
def water_plants():
    try:
        client = mqtt.Client()
        client.tls_set()
        client.username_pw_set(mqtt_user, mqtt_password)
        client.connect(mqtt_broker_connection, port, 60)

        client.loop_start()
        result = client.publish("smartfarm/pump_command", "on")
        print("Publish result code:", result.rc)
        time.sleep(1)
        client.loop_stop()
        client.disconnect()

        return redirect(url_for("index", watered="yes"))
    except Exception as e:
        print("Error in water_plants route:", e)
        return redirect(url_for("index", watered="error"))

