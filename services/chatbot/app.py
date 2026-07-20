"""
MafurikoAI - Chatbot Microservice
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

WEATHER_SERVICE = os.getenv('WEATHER_SERVICE_URL', 'http://localhost:5002')
ML_SERVICE = os.getenv('ML_SERVICE_URL', 'http://localhost:5003')


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "service": "chatbot-service",
        "status": "healthy",
        "port": os.getenv('PORT', 5004)
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').strip().lower()
    location = data.get('location', 'Nairobi')
    language = data.get('language', 'en')
    
    intent = detect_intent(message)
    
    if intent == 'greeting':
        return jsonify({
            "text": get_greeting(language),
            "type": "greeting",
            "intent": intent
        })
    
    elif intent == 'weather':
        try:
            city = extract_city(message) or location
            response = requests.get(f"{WEATHER_SERVICE}/api/weather/{city}", timeout=5)
            weather = response.json()
            
            return jsonify({
                "text": f"🌧️ Current weather in {weather['city']}",
                "type": "weather",
                "intent": intent,
                "weather": weather
            })
        except Exception as e:
            return jsonify({
                "text": f"Weather service error: {str(e)}",
                "type": "error"
            })
    
    elif intent == 'flood_check':
        try:
            weather_resp = requests.get(f"{WEATHER_SERVICE}/api/weather/{location}", timeout=5)
            weather = weather_resp.json()
            
            road = extract_road(message) or "your location"
            
            pred_resp = requests.post(
                f"{ML_SERVICE}/api/predict",
                json={
                    "road": road,
                    "location": location,
                    "weather": weather
                },
                timeout=5
            )
            prediction = pred_resp.json()
            
            return jsonify({
                "text": f"Flood risk on {road}: {prediction['risk_level'].upper()}",
                "type": "prediction",
                "intent": intent,
                "prediction": prediction,
                "weather": weather
            })
        except Exception as e:
            return jsonify({
                "text": f"Prediction error: {str(e)}",
                "type": "error"
            })
    
    elif intent == 'emergency':
        return jsonify({
            "text": get_emergency(language),
            "type": "emergency",
            "intent": intent
        })
    
    else:
        return jsonify({
            "text": "I can help with weather, floods, or emergency info!",
            "type": "unknown"
        })


def detect_intent(message):
    intents = {
        'greeting': ['hello', 'hi', 'hey', 'habari', 'jambo'],
        'weather': ['weather', 'rain', 'temperature', 'mvua', 'hali'],
        'flood_check': ['flood', 'safe', 'road', 'risk', 'salama'],
        'emergency': ['emergency', 'help', 'dharura']
    }
    for intent, keywords in intents.items():
        if any(kw in message for kw in keywords):
            return intent
    return 'unknown'


def get_greeting(lang):
    if lang == 'sw':
        return "👋 Habari! Mimi ni MafurikoAI. Naweza kukusaidia?"
    return "👋 Hello! I'm MafurikoAI. How can I help you today?"


def get_emergency(lang):
    if lang == 'sw':
        return "🚨 DHARURA:\n🚔 Polisi: 999\n🏥 Red Cross: 1199"
    return "🚨 EMERGENCY:\n🚔 Police: 999\n🏥 Red Cross: 1199"


def extract_road(message):
    roads = ['Thika Road', 'Mombasa Road', 'Waiyaki Way', 'Ngong Road',
             'Jogoo Road', 'Outer Ring Road', 'Uhuru Highway']
    for road in roads:
        if road.lower() in message:
            return road
    return None


def extract_city(message):
    cities = ['nairobi', 'mombasa', 'kisumu', 'nakuru', 'eldoret']
    for city in cities:
        if city in message:
            return city.title()
    return None


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5004))
    print(f"💬 Chatbot Service starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)