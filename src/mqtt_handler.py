# mqtt_handler.py

import paho.mqtt.client as mqtt
from src.vehiclestate import VehicleState
import threading
import wx

class MQTTHandler:
    def __init__(self, textctrl:wx.TextCtrl, vehicle_state: VehicleState):
        self.broker_address = None
        self.port = 1883
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.textctrl = textctrl
        self.vehicle_state = vehicle_state
        self.topics = ["rocky/position", "rocky/arm/1", "rocky/arm/2"]

    def on_connect(self, client:mqtt.Client, userdata, flags, reason_code, properties):
        client.subscribe([(topic, 0) for topic in self.topics])
        #client.publish("test/cenfra", "Interface connected.")
        #client.publish("rocky/position", "Interface connected222.")
    
    def on_message(self, client, userdata, msg):
        # get message data
        topic = msg.topic
        message = msg.payload.decode("utf-8")
        # add message to mqtt log
        self.textctrl.AppendText(f"{topic} {message}\n")
        # update vehicle state with data
        if topic == "rocky/position":
            x, y, z = message.split(' ')
            x, y, z = float(x), float(y), float(z)
            self.vehicle_state.add_position([x, y, z])

    def SetBrokerAddress(self, value:str):
        self.broker_address = value

    def connect(self) -> bool:
        try:
            self.client.connect(self.broker_address, self.port, 60)
            self.thread = threading.Thread(target=self.client.loop_forever)
            self.thread.daemon = True
            self.thread.start()
        except ConnectionRefusedError:
            print("connection refused")
            return False
        except Exception as e:
            print(e)
            return False
        return True

    def disconnect(self):
        self.client.disconnect()
        self.thread.join(timeout=1.0)