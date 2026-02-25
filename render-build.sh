#!/usr/bin/env bash
# exit on error
set -o errexit

# Installation des dépendances Python
pip install -r requirements.txt

# Installation de Playwright et de ses navigateurs
# On force l'installation de Chromium spécifiquement
python -m playwright install chromium

# OPTIONNEL : Si Render se plaint encore de librairies manquantes (.so), 
# décommente la ligne suivante (attention, peut être lent au build)
# python -m playwright install-deps chromium