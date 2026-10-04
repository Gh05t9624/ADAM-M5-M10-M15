# app/engine/selector.py

def select_top_markets(snapshot, max_markets=5):
    autorised = [
        (symbol, data)
        for symbol, data in snapshot.items()
        if data["statut"] == "AUTORISÉ"
    ]

    # Tri par score décroissant
    autorised.sort(key=lambda x: x[1]["score"], reverse=True)

    return autorised[:max_markets]
