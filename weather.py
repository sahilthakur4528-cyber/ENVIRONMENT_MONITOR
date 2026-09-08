# ==========================================
# Weather Module
# ==========================================

import requests

from config import OPENWEATHER_API_KEY


# ==========================================
# GET WEATHER BY CITY
# ==========================================

def get_weather(city):

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {

        "q": city,

        "appid": OPENWEATHER_API_KEY,

        "units": "metric"

    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()


        weather = {

            "city": data["name"],

            "temperature": round(
                data["main"]["temp"],
                1
            ),

            "humidity": data["main"]["humidity"],

            "condition":
                data["weather"][0]["main"],

            "description":
                data["weather"][0]["description"],

            "wind_speed":
                data["wind"]["speed"]

        }

        return weather


    except Exception as e:

        print(
            "Weather Error:",
            e
        )

        return None


# ==========================================
# GET WEATHER BY LIVE LOCATION
# ==========================================

def get_weather_by_coordinates(lat, lon):

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {

        "lat": lat,

        "lon": lon,

        "appid": OPENWEATHER_API_KEY,

        "units": "metric"

    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()


        weather = {

            "city": data["name"],

            "temperature": round(
                data["main"]["temp"],
                1
            ),

            "humidity": data["main"]["humidity"],

            "condition":
                data["weather"][0]["main"],

            "description":
                data["weather"][0]["description"],

            "wind_speed":
                data["wind"]["speed"]

        }

        return weather


    except Exception as e:

        print(
            "Weather Location Error:",
            e
        )

        return None