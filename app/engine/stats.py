# app/engine/stats.py
import csv
from collections import defaultdict


class StatsEngine:

    def __init__(self, journal_path: str):
        self.journal_path = journal_path

    def compute(self):
        trades = []

        try:
            with open(self.journal_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    trades.append(row)
        except FileNotFoundError:
            return self._empty()

        total = len(trades)
        authorized = sum(1 for t in trades if t["statut"] == "AUTORISÉ")

        by_symbol = defaultdict(int)
        by_direction = defaultdict(int)

        wins = 0
        losses = 0

        for t in trades:
            by_symbol[t["symbol"]] += 1
            by_direction[t["direction"]] += 1

            if t.get("outcome") == "GAIN":
                wins += 1
            elif t.get("outcome") == "PERTE":
                losses += 1

        winrate = round(wins / max(1, wins + losses) * 100, 1)

        return {
            "total_trades": total,
            "authorized": authorized,
            "wins": wins,
            "losses": losses,
            "winrate": winrate,
            "by_symbol": dict(by_symbol),
            "by_direction": dict(by_direction),
        }

    def _empty(self):
        return {
            "total_trades": 0,
            "authorized": 0,
            "wins": 0,
            "losses": 0,
            "winrate": 0,
            "by_symbol": {},
            "by_direction": {},
        }
