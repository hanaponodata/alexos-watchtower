"""
selfaudit/analyzers/protocol.py
Enterprise-grade protocol analyzer for Watchtower self-audit engine.
Assesses registered symbolic protocols, plugin/extension health, version conflicts, and compliance.
"""

from typing import Dict, Any, List
from plugins.manager import PluginConfig
import pkg_resources

class ProtocolAnalyzer:
    def __init__(self):
        self.plugin_config = PluginConfig()

    def analyze(self) -> Dict[str, Any]:
        results = {
            "enabled_plugins": [],
            "disabled_plugins": [],
            "plugin_issues": [],
            "version_conflicts": [],
            "compliance_failures": [],
            "protocol_status": "healthy",
            "warnings": []
        }

        for plugin in self.plugin_config.list_plugins():
            cfg = self.plugin_config.get_plugin_config(plugin)
            if self.plugin_config.is_enabled(plugin):
                results["enabled_plugins"].append(plugin)
            else:
                results["disabled_plugins"].append(plugin)
            # Version and compliance checks
            if cfg:
                # Check for missing version or outdated plugin
                version = cfg.get("version", "0.0.0")
                try:
                    pkg_resources.parse_version(version)
                except Exception:
                    results["plugin_issues"].append(f"Plugin {plugin} has invalid version format: {version}")
                # Compliance example: check if required fields exist
                for required in ["name", "author"]:
                    if not cfg.get(required):
                        results["compliance_failures"].append(f"Plugin {plugin} missing required field: {required}")
        # Example: check for duplicate or conflicting plugins
        if len(set(results["enabled_plugins"])) != len(results["enabled_plugins"]):
            results["version_conflicts"].append("Duplicate enabled plugin names detected.")

        if results["plugin_issues"] or results["version_conflicts"] or results["compliance_failures"]:
            results["protocol_status"] = "review"
            if results["plugin_issues"]:
                results["warnings"].append(f"Plugin issues: {results['plugin_issues']}")
            if results["version_conflicts"]:
                results["warnings"].append(f"Version conflicts: {results['version_conflicts']}")
            if results["compliance_failures"]:
                results["warnings"].append(f"Compliance failures: {results['compliance_failures']}")

        return results

if __name__ == "__main__":
    analyzer = ProtocolAnalyzer()
    print(analyzer.analyze())
