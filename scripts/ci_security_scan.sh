#!/bin/bash
set -e
# OWASP ZAP
zap-baseline.py -t http://localhost:8000 -r zap_report.html
# Semgrep
semgrep --config=auto .
# Bandit
bandit -r . 