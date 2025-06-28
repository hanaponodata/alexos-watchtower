"""
utils/loader.py
Enterprise-grade dynamic loader utilities for Watchtower.
Handles dynamic module, class, and object loading for plugin, protocol, and extension support.
"""

import importlib
import sys
from types import ModuleType
from typing import Optional, Any

class LoaderUtils:
    @staticmethod
    def load_module(module_path: str) -> Optional[ModuleType]:
        try:
            if module_path in sys.modules:
                return sys.modules[module_path]
            return importlib.import_module(module_path)
        except Exception as e:
            print(f"[LoaderUtils] Error loading module {module_path}: {e}")
            return None

    @staticmethod
    def load_class(module_path: str, class_name: str) -> Optional[Any]:
        module = LoaderUtils.load_module(module_path)
        if module and hasattr(module, class_name):
            return getattr(module, class_name)
        print(f"[LoaderUtils] Class {class_name} not found in {module_path}")
        return None

if __name__ == "__main__":
    mod = LoaderUtils.load_module("os")
    print("os module loaded:", mod is not None)
    cls = LoaderUtils.load_class("datetime", "datetime")
    print("datetime class loaded:", cls)
