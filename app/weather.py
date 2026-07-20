"""OpenWeatherMap API Integration"""
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class WeatherAPI:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "")
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def get_weather(self, city="Nairobi"):
        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": f"{city},KE",
                "appid": self.api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "city": data["name"],
                    "temperature_c": round(data["main"]["temp"], 1),
                    "humidity_percent": data["main"]["humidity"],
                    "rainfall_mm": data.get("rain", {}).get("1h", 0),
                    "weather_description": data["weather"][0]["description"].title(),
                    "weather_icon": data["weather"][0]["icon"],
                    "wind_speed_ms": data["wind"]["speed"],
                    "pressure_hpa": data["main"]["pressure"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "is_mock": False
                }
            return self._mock_weather(city)
        except Exception as e:
            print(f"Weather API error: {e}")
            return self._mock_weather(city)
    
    def _mock_weather(self, city):
        import random
        month = datetime.now().month
        is_rainy = month in [3, 4, 5, 10, 11, 12]
        rainfall = random.uniform(15, 85) if is_rainy else random.uniform(0, 10)
        
        return {
            "success": True,
            "city": city,
            "temperature_c": round(random.uniform(18, 26), 1),
            "humidity_percent": random.randint(60, 90) if is_rainy else random.randint(40, 65),
            "rainfall_mm": round(rainfall, 1),
            "weather_description": "Heavy Rain" if rainfall > 40 else "Light Rain" if rainfall > 5 else "Scattered Clouds",
            "weather_icon": "10d" if rainfall > 5 else "02d",
            "wind_speed_ms": round(random.uniform(1, 8), 1),
            "pressure_hpa": random.randint(1010, 1025),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "is_mock": True
        }