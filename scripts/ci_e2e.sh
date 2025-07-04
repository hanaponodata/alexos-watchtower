#!/bin/bash
set -e
# Electron E2E
cd chainbot-gui && npx playwright test
cd ..
# GTK4 E2E
cd ui/gnome && pytest tests/test_e2e.py 