from flask import Flask, render_template, request
import requests
from geopy.geocoders import Nominatim
from datetime import datetime

app = Flask(__name__)

# Получение координат по городу
def get_coordinates(city):
    geolocator = Nominatim(user_agent="weather_client")
    location = geolocator.geocode(city)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Получение прогноза
def get_weather(latitude, longitude, date):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
        "start_date": date,
        "end_date": date
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "daily" not in data:
        return None

    daily = data["daily"]
    return {
        "date": daily["time"][0],
        "temp_min": daily["temperature_2m_min"][0],
        "temp_max": daily["temperature_2m_max"][0],
        "precipitation": daily["precipitation_sum"][0]
    }

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        city = request.form["city"]
        date = request.form["date"]

        lat, lon = get_coordinates(city)
        if lat:
            weather = get_weather(lat, lon, date)
            if weather:
                result = {
                    "city": city,
                    "date": weather["date"],
                    "temp_min": weather["temp_min"],
                    "temp_max": weather["temp_max"],
                    "precipitation": weather["precipitation"]
                }
            else:
                result = {"error": "Прогноз недоступен"}
        else:
            result = {"error": "Город не найден"}

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
