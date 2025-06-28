"""
messagebus/kafka.py
Enterprise-grade Kafka message bus adapter for Watchtower.
Handles publish/subscribe, partitioned topics, and event streaming via Kafka.
"""

from typing import Callable, Optional, Any, List
from kafka import KafkaProducer, KafkaConsumer

class KafkaBus:
    def __init__(self, brokers: Optional[List[str]] = None, group_id: str = "watchtower"):
        self.brokers = brokers or ["localhost:9092"]
        self.group_id = group_id
        self.producer = KafkaProducer(bootstrap_servers=self.brokers)
        self.consumers = {}

    def publish(self, topic: str, value: bytes):
        self.producer.send(topic, value=value)
        self.producer.flush()

    def subscribe(self, topic: str, cb: Callable[[Any], None]):
        consumer = KafkaConsumer(
            topic,
            group_id=self.group_id,
            bootstrap_servers=self.brokers,
            auto_offset_reset='earliest'
        )
        self.consumers[topic] = consumer
        for msg in consumer:
            cb(msg)

    def close(self):
        self.producer.close()
        for consumer in self.consumers.values():
            consumer.close()

if __name__ == "__main__":
    print("KafkaBus requires a running Kafka cluster and kafka-python installed.")
