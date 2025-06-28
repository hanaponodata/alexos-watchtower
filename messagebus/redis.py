"""
messagebus/redis.py
Enterprise-grade Redis Streams/PubSub adapter for Watchtower message bus.
Handles event streaming, publish/subscribe, and persistence via Redis.
"""

import redis
from typing import Callable, Optional

class RedisBus:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.client = redis.StrictRedis(host=host, port=port, db=db, decode_responses=True)

    def publish(self, channel: str, message: str):
        self.client.publish(channel, message)

    def subscribe(self, channel: str, cb: Callable[[str], None]):
        pubsub = self.client.pubsub()
        pubsub.subscribe(channel)
        for msg in pubsub.listen():
            if msg["type"] == "message":
                cb(msg["data"])

    def xadd(self, stream: str, data: dict):
        self.client.xadd(stream, data)

    def xread(self, stream: str, last_id: str = "$", count: int = 10):
        return self.client.xread({stream: last_id}, count=count)

    def close(self):
        self.client.close()

if __name__ == "__main__":
    print("RedisBus requires a running Redis server and redis-py installed.")
