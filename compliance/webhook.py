"""
compliance/webhook.py
Enterprise-grade webhook notifier for Watchtower compliance and alerting.
Delivers structured event, log, or alert data to external endpoints.
"""

from typing import Dict, Any, Optional
import requests
import logging

class WebhookNotifier:
    def __init__(self, url: str, api_key: Optional[str] = None):
        self.url = url
        self.api_key = api_key
        self.logger = logging.getLogger("watchtower.compliance.webhook")

    def notify(self, payload: Dict[str, Any]) -> bool:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        try:
            resp = requests.post(self.url, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            self.logger.info(f"Webhook notification sent: {payload}")
            return True
        except Exception as e:
            self.logger.error(f"Webhook notification failed: {e}")
            return False

if __name__ == "__main__":
    wh = WebhookNotifier(url="http://localhost:8000/webhook")
    print("Sent:", wh.notify({"alert": "test"}))
