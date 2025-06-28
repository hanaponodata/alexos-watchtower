"""
upgrade/hooks.py
Enterprise-grade upgrade hooks for Watchtower.
Handles pre/post upgrade triggers, integration points for ChainBot/Harry, and event bus notifications.
"""

from typing import Callable, List, Dict, Any

class UpgradeHooks:
    def __init__(self):
        self.pre_upgrade_hooks: List[Callable[[Dict[str, Any]], None]] = []
        self.post_upgrade_hooks: List[Callable[[Dict[str, Any]], None]] = []

    def register_pre_hook(self, func: Callable[[Dict[str, Any]], None]):
        self.pre_upgrade_hooks.append(func)

    def register_post_hook(self, func: Callable[[Dict[str, Any]], None]):
        self.post_upgrade_hooks.append(func)

    def trigger_pre_hooks(self, context: Dict[str, Any]):
        for hook in self.pre_upgrade_hooks:
            try:
                hook(context)
            except Exception as e:
                print(f"[UpgradeHooks] Pre-upgrade hook error: {e}")

    def trigger_post_hooks(self, context: Dict[str, Any]):
        for hook in self.post_upgrade_hooks:
            try:
                hook(context)
            except Exception as e:
                print(f"[UpgradeHooks] Post-upgrade hook error: {e}")

if __name__ == "__main__":
    hooks = UpgradeHooks()
    print("UpgradeHooks ready for pre/post-upgrade trigger registration.")
