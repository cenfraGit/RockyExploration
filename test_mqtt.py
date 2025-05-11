import paho.mqtt.client as mqtt

# Broker details
broker_address = "192.168.100.31"  # Replace with your broker IP if needed
port = 1883
topic = "test/cenfra"
message = "Hello from Python!"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT Broker at {broker_address}:{port}")
        client.publish(topic, message)
        print(f"Published message: '{message}' to topic '{topic}'")
        client.disconnect()  # Disconnect after publishing (for this simple example)
    else:
        print(f"Failed to connect, return code {rc}")

client = mqtt.Client()
client.on_connect = on_connect

try:
    client.connect(broker_address, port, 60)  # Connect to the broker
    client.loop_forever()  # Keep the script running to handle connection
except ConnectionRefusedError:
    print(f"Error: Connection to {broker_address}:{port} refused. Make sure the Mosquitto broker is running.")
except Exception as e:
    print(f"An error occurred: {e}")