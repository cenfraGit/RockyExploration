# mqtt_handler.py

import paho.mqtt.client as mqtt
import threading
import wx

class MQTTHandler:
    def __init__(self, textctrl:wx.TextCtrl):
        self.broker_address = None
        self.port = 1883
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.textctrl = textctrl

    def on_connect(self, client:mqtt.Client, userdata, flags, reason_code, properties):
        client.subscribe("test/cenfra")
        client.publish("test/cenfra", "Interface connected.")
    
    def on_message(self, client, userdata, msg):
        message = f"{msg.topic} {msg.payload.decode("utf-8")}\n"
        self.textctrl.AppendText(message)

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