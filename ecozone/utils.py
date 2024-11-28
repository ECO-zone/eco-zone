from datetime import datetime, timedelta


def round_date_to_quarter_hour(date: datetime) -> datetime:
    hour_ratio = date.minute / 60
    if hour_ratio < 0.25:
        minutes = 0
    elif hour_ratio < 0.5:
        minutes = 15
    elif hour_ratio < 0.75:
        minutes = 30
    else:
        minutes = 45

    return date + timedelta(minutes=minutes - date.minute)
