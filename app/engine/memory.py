# app/engine/memory.py
import json
import os
from datetime import datetime

SCAN_PATH = "app/data/scans/last_scan.json"


def load_last_scan():
    if not os.path.exists(SCAN_PATH):
        return {}
    with open(SCAN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_scan(scan):
    os.makedirs(os.path.dirname(SCAN_PATH), exist_ok=True)
    with open(SCAN_PATH, "w", encoding="utf-8") as f:
        json.dump(scan, f, indent=2)


def build_snapshot(results):
    snapshot = {}
    for symbol, result in results.items():
        snapshot[symbol] = {
            "statut": result["statut"],
            "direction": result["direction"],
            "score": result["score"],
            "time": datetime.utcnow().isoformat()
        }
    return snapshot


def compare_scans(prev, current):
    changes = {
        "NEW_AUTORISE": [],
        "DEGRADATION": [],
        "REJET": []
    }

    for symbol, curr in current.items():
        old = prev.get(symbol)

        if not old:
            continue

        if old["statut"] != "AUTORISÉ" and curr["statut"] == "AUTORISÉ":
            changes["NEW_AUTORISE"].append(symbol)

        elif old["statut"] == "AUTORISÉ" and curr["statut"] != "AUTORISÉ":
            changes["DEGRADATION"].append(symbol)

        elif curr["statut"] == "INTERDIT":
            changes["REJET"].append(symbol)

    return changes
