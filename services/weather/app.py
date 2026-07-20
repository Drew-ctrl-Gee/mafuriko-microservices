"""
MafurikoAI - Weather Microservice
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "service": "weather-service",
        "status": "healthy",
        "port": os.getenv('PORT', 5002)
    })


@app.route('/api/weather/<city>', methods=['GET'])
def get_weather(city):
    api_key = os.getenv('7b6385a21323babda268827bf3f33ae1', '')
    
    if not api_key:
        return jsonify(_mock_weather(city))
    
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": f"{city},KE",
            "appid": api_key,
            "units": "metric"
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                "success": True,
                "city": data["name"],
                "temperature_c": round(data["main"]["temp"], 1),
                "humidity_percent": data["main"]["humidity"],
                "rainfall_mm": data.get("rain", {}).get("1h", 0),
                "weather_description": data["weather"][0]["description"].title(),
                "wind_speed_ms": data["wind"]["speed"],
                "pressure_hpa": data["main"]["pressure"],
                "timestamp": datetime.now().isoformat()
            })
    except Exception as e:
        print(f"Weather API error: {e}")
    
    return jsonify(_mock_weather(city))


def _mock_weather(city):
    import random
    return {
        "success": True,
        "city": city,
        "temperature_c": round(random.uniform(18, 28), 1),
        "humidity_percent": random.randint(50, 85),
        "rainfall_mm": round(random.uniform(0, 30), 1),
        "weather_description": "Partly Cloudy",
        "wind_speed_ms": round(random.uniform(1, 8), 1),
        "pressure_hpa": random.randint(1010, 1025),
        "timestamp": datetime.now().isoformat(),
        "is_mock": True
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    print(f"🌦️ Weather Service starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)