from datetime import datetime
import pytz

def get_local_time(language):
    if language == "Spanish":
        tz = pytz.timezone("Europe/Madrid")
        city = "Madrid"
    elif language == "French":
        tz = pytz.timezone("Europe/Paris")
        city = "Paris"
    else:
        tz = pytz.timezone("UTC")
        city = "Unknown"

    now = datetime.now(tz)

    return {
        "city": city,
        "time": now.strftime("%H:%M:%S"),
        "date": now.strftime("%Y-%m-%d")
    }