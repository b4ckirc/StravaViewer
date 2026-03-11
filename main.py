#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════╗
║       STRAVA ACTIVITY VIEWER  •  v3.0               ║
║  Analisi, libreria e download corse da Strava        ║
╚══════════════════════════════════════════════════════╝

INSTALLAZIONE DIPENDENZE:
    pip install matplotlib folium pillow tkinterweb pymongo requests

AVVIO:
    python main.py

REQUISITI OPZIONALI:
  - Docker Desktop (per MongoDB automatico)
  - Account sviluppatore Strava (per il download)
    → https://www.strava.com/settings/api
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def _check_deps():
    missing = []
    try:    import matplotlib
    except: missing.append("matplotlib")
    try:    import folium
    except: missing.append("folium")
    try:    import tkinterweb
    except: missing.append("tkinterweb")
    try:    import pymongo
    except: missing.append("pymongo")
    try:    import requests
    except: missing.append("requests")
    if missing:
        print(f"⚠️  Librerie opzionali mancanti: {', '.join(missing)}")
        print(f"   pip install {' '.join(missing)}\n")

if __name__ == "__main__":
    _check_deps()
    from ui.app import StravaApp
    app = StravaApp()
    app.mainloop()
