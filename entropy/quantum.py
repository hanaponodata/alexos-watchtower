"""
entropy/quantum.py
Enterprise-grade quantum entropy source for Watchtower.
Pulls randomness from online quantum entropy APIs or integrated QKD hardware.
"""

from typing import Optional
import requests

class QuantumEntropy:
    def __init__(self, api_url: str = "https://qrng.anu.edu.au/API/jsonI.php?length=1&type=uint8"):
        self.api_url = api_url

    def get_entropy(self) -> Optional[int]:
        try:
            resp = requests.get(self.api_url, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if "data" in data and isinstance(data["data"], list) and data["data"]:
                return int(data["data"][0])
        except Exception as e:
            print(f"[QuantumEntropy] Error fetching quantum entropy: {e}")
        return None

if __name__ == "__main__":
    qe = QuantumEntropy()
    print("Quantum entropy sample:", qe.get_entropy())
