"""
messagebus/zeromq.py
Enterprise-grade ZeroMQ message bus adapter for Watchtower.
Supports publish/subscribe, push/pull, and request/reply patterns via ZeroMQ.
"""

import zmq
from typing import Callable, Optional

class ZeroMQBus:
    def __init__(self, zmq_url: str = "tcp://127.0.0.1:5555", mode: str = "pub"):
        self.zmq_url = zmq_url
        self.mode = mode
        self.context = zmq.Context()
        if mode == "pub":
            self.socket = self.context.socket(zmq.PUB)
        elif mode == "sub":
            self.socket = self.context.socket(zmq.SUB)
        elif mode == "push":
            self.socket = self.context.socket(zmq.PUSH)
        elif mode == "pull":
            self.socket = self.context.socket(zmq.PULL)
        else:
            self.socket = self.context.socket(zmq.REQ)
        self.socket.bind(zmq_url) if mode in ("pub", "push", "req") else self.socket.connect(zmq_url)

    def publish(self, topic: str, message: str):
        if self.mode == "pub":
            self.socket.send_string(f"{topic} {message}")

    def subscribe(self, topic: str, cb: Callable[[str, str], None]):
        if self.mode == "sub":
            self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)
            while True:
                msg = self.socket.recv_string()
                t, m = msg.split(" ", 1)
                cb(t, m)

    def send(self, message: str):
        if self.mode == "push":
            self.socket.send_string(message)

    def receive(self, cb: Callable[[str], None]):
        if self.mode == "pull":
            while True:
                msg = self.socket.recv_string()
                cb(msg)

    def close(self):
        self.socket.close()
        self.context.term()

if __name__ == "__main__":
    print("ZeroMQBus requires pyzmq and a running ZeroMQ endpoint.")
