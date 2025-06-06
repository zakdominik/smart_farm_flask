connect_to_wifi()
connect_to_mqtt()
initialize_lcd()
initialize_pins()

start = input() #True/False

def runSystem():
    displayValues()
    send_data_to_mqtt()
    should_water = read_data_mqtt(pump_command)

while start:
    runSystem()
    if shouldWater:
        displayMessage()
        pump_on(0.5s)
        send_data_to_mqtt()
    if water<threshold:
        displayWarning()



