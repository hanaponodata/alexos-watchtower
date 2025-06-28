"""
messagebus/__init__.py
Message bus and orchestration package initializer for Watchtower.
Exposes adapters for NATS, MQTT, Kafka, ZeroMQ, Redis, and core hooks.
"""

from .nats import NATSBus
from .mqtt import MQTTBus
from .kafka import KafkaBus
from .zeromq import ZeroMQBus
from .redis import RedisBus
from .hooks import MessageBusHooks

__all__ = [
    "NATSBus",
    "MQTTBus",
    "KafkaBus",
    "ZeroMQBus",
    "RedisBus",
    "MessageBusHooks"
]
