# mqtt_handler.py

import paho.mqtt.client as mqtt
import threading

class MQTTHandler:
    def __init__(self):
        self.broker_address = None
        self.port = 1883
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client:mqtt.Client, userdata, flags, reason_code, properties):
        client.subscribe("test/cenfra")
        client.publish("test/cenfra", "hi")
    
    def on_message(self, client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))

    def SetBrokerAddress(self, value:str):
        self.broker_address = value

    def connect(self):
        try:
            self.client.connect(self.broker_address, self.port, 60)
            self.thread = threading.Thread(target=self.client.loop_forever)
            self.thread.daemon = True
            self.thread.start()
        except ConnectionRefusedError:
            print("connection refused")
        except Exception as e:
            print(e)

    def disconnect(self):
        self.client.disconnect()
        self.thread.join(timeout=1.0)