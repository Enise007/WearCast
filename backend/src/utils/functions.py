import os

import requests
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
IP_API_KEY = os.getenv("IP_API_KEY")

def get_geolocation(client_ip):
    base = f"https://api.ipgeolocation.io/v2/ipgeo?apiKey={IP_API_KEY}"
    url = f"{base}&ip={client_ip}" if client_ip else base
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    return r.json()


def get_open_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=tr"
    response = requests.get(url)
    weather_data = response.json()
    formatted_weather = f"Weather: {weather_data['weather'][0]['description']}, Temperature: {weather_data['main']['temp']}°C, wind speed: {weather_data['wind']['speed']} m/s"
    return formatted_weather

def get_motivational_quote():
    url = "https://zenquotes.io/api/random"

    response = requests.get(url)
    data = response.json()

    quote = data[0]["q"]
    author = data[0]["a"]

    return f'"{quote}" — {author}'
