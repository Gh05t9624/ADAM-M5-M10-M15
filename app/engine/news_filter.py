from datetime import datetime

# 🔥 Heures critiques (UTC)
HIGH_IMPACT_NEWS = [
    (13, 14),  # US CPI / NFP approx
    (8, 9),    # London news
]

def is_news_time():
    """
    Filtre de news beaucoup moins restrictif
    Bloque uniquement pendant les 30 minutes critiques autour des news majeures
    """
    hour = datetime.utcnow().hour
    minute = datetime.utcnow().minute

    # Ne bloquer que pendant 30 minutes critiques (xx:00-xx:30)
    for start, end in HIGH_IMPACT_NEWS:
        if hour == start and minute < 30:
            return True
        elif hour == end and minute < 30:
            return True

    return False