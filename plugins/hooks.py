"""
plugins/hooks.py
Enterprise-grade plugin extension hooks for Watchtower.
Allows core and third-party modules to register and trigger plugin-defined actions at runtime.
"""

from typing import Callable, Dict, List, Any

class PluginHooks:
    def __init__(self):
        self.hooks: Dict[str, List[Callable[..., Any]]] = {}

    def register_hook(self, hook_name: str, func: Callable[..., Any]):
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(func)

    def trigger_hooks(self, hook_name: str, *args, **kwargs):
        results = []
        for func in self.hooks.get(hook_name, []):
            try:
                results.append(func(*args, **kwargs))
            except Exception as e:
                print(f"[PluginHooks] Hook {hook_name} error: {e}")
        return results

    def list_hooks(self) -> Dict[str, int]:
        return {k: len(v) for k, v in self.hooks.items()}

if __name__ == "__main__":
    hooks = PluginHooks()
    print("PluginHooks initialized.")
