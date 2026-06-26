import requests

LOCATIONS = {
    "Spanish": {
        "city": "Madrid",
        "lat": 40.4168,
        "lon": -3.7038
    },
    "French": {
        "city": "Paris",
        "lat": 48.8566,
        "lon": 2.3522
    }
}


def get_weather(language):

    try:
        location = LOCATIONS[language]

        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={location['lat']}"
            f"&longitude={location['lon']}"
            f"&current=temperature_2m,weather_code,wind_speed_10m"
        )

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "city": location["city"],
            "temperature": data["current"]["temperature_2m"],
            "wind": data["current"]["wind_speed_10m"],
        }

    except Exception:
        return {
            "city": "Coming soon",
            "temperature": None,
            "wind": None,
        }