"""
messagebus/mqtt.py
Enterprise-grade MQTT message bus adapter for Watchtower.
Handles publish/subscribe and event flow via MQTT brokers.
"""

from typing import Callable, Optional
import paho.mqtt.client as mqtt

class MQTTBus:
    def __init__(self, host: str = "localhost", port: int = 1883, client_id: str = "watchtower"):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.client = mqtt.Client(client_id)
        self._on_message_cb = None

    def connect(self):
        self.client.connect(self.host, self.port, 60)

    def publish(self, topic: str, payload: str):
        self.client.publish(topic, payload)

    def subscribe(self, topic: str, cb: Callable):
        self._on_message_cb = cb
        self.client.subscribe(topic)
        self.client.on_message = self._on_message

    def _on_message(self, client, userdata, msg):
        if self._on_message_cb:
            self._on_message_cb(msg.topic, msg.payload.decode())

    def loop_forever(self):
        self.client.loop_forever()

    def disconnect(self):
        self.client.disconnect()

if __name__ == "__main__":
    print("MQTTBus requires a running MQTT broker and paho-mqtt installed.")
