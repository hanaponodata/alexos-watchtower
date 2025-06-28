"""
entropy/hwrng.py
Enterprise-grade hardware RNG (hwrng) adapter for Watchtower.
Pulls entropy directly from OS hardware devices (/dev/hwrng, /dev/random).
"""

from typing import Optional

class HardwareRNG:
    def __init__(self, device: str = "/dev/hwrng"):
        self.device = device

    def get_entropy(self, num_bytes: int = 1) -> Optional[bytes]:
        try:
            with open(self.device, "rb") as f:
                return f.read(num_bytes)
        except Exception as e:
            print(f"[HardwareRNG] Error reading entropy from {self.device}: {e}")
            return None

    def random_int(self, min_val: int = 0, max_val: int = 255) -> Optional[int]:
        ent = self.get_entropy(1)
        if ent is not None and len(ent) == 1:
            val = ent[0]
            # Map val (0-255) into min_val..max_val
            scale = max_val - min_val + 1
            return min_val + (val % scale)
        return None

if __name__ == "__main__":
    rng = HardwareRNG()
    print("Hardware entropy sample:", rng.get_entropy())
    print("Random int sample:", rng.random_int(1, 100))
