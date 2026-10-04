# app/journal/trade_journal.py
import csv
import os
from datetime import datetime


class TradeJournal:

    def __init__(self, path="journal_trades.csv"):
        self.path = path
        self._init_file()

    def _init_file(self):
        if not os.path.exists(self.path):
            with open(self.path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp",
                    "symbol",
                    "direction",
                    "score",
                    "timeframe",
                    "statut",
                    "outcome"
                ])

    def log(self, symbol, result, timeframe="M5"):
        if result["statut"] != "AUTORISÉ":
            return

        with open(self.path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.utcnow().isoformat(),
                symbol,
                result["direction"],
                result["score"],
                timeframe,
                result["statut"],
                result.get("outcome", "NEUTRE")
                
            ])

    @property
    def trades(self):
        # """Retourne tous les trades du journal sous forme de liste de dicts"""
        trades = []

        if not os.path.exists(self.path):
            return trades

        with open(self.path, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                trades.append({
                    "timestamp": row["timestamp"],
                    "symbol": row["symbol"],
                    "direction": row["direction"],
                    "score": float(row["score"]),
                    "timeframe": row["timeframe"],
                    "statut": row["statut"]
                })

        return trades

    def log_outcome(self, symbol, result, outcome):
        with open(self.path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.utcnow().isoformat(),
                symbol,
                result["direction"],
                result["score"],
                "M5",
                result["statut"],
                outcome
            ])
