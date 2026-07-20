"""MafurikoAI Chatbot Brain"""
from datetime import datetime


class Chatbot:
    def __init__(self, predictor, weather_api):
        self.predictor = predictor
        self.weather = weather_api
        
        self.intents = {
            "greeting": ["hello", "hi", "hey", "habari", "hujambo", "mambo", "sasa", "jambo"],
            "flood_check": ["flood", "flooded", "mafuriko", "safe", "salama", "risk", "hatari"],
            "weather": ["weather", "hali", "rain", "mvua", "temperature", "joto"],
            "route": ["route", "njia", "alternative", "avoid", "epuka"],
            "emergency": ["emergency", "dharura", "help", "trapped", "stuck"],
            "tips": ["tip", "advice", "ushauri", "safety", "usalama", "how"],
            "goodbye": ["bye", "goodbye", "kwaheri", "baadaye", "thanks", "asante"]
        }
    
    def detect_language(self, text):
        swahili_words = ["mafuriko", "mvua", "njia", "habari", "hujambo",
                        "salama", "hatari", "kwaheri", "asante", "msaada"]
        return "sw" if any(w in text.lower() for w in swahili_words) else "en"
    
    def detect_intent(self, message):
        message_lower = message.lower()
        scores = {}
        
        for intent, keywords in self.intents.items():
            scores[intent] = sum(1 for kw in keywords if kw in message_lower)
        
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "unknown"
    
    def get_response(self, message, user_location="Nairobi", language="auto"):
        if language == "auto":
            language = self.detect_language(message)
        
        intent = self.detect_intent(message)
        
        if intent == "greeting":
            return self._greeting(language)
        elif intent == "flood_check" or intent == "route":
            return self._check_flood(message, user_location, language)
        elif intent == "weather":
            return self._get_weather_info(message, user_location, language)
        elif intent == "emergency":
            return self._emergency_info(language)
        elif intent == "tips":
            return self._safety_tips(language)
        elif intent == "goodbye":
            return self._goodbye(language)
        else:
            return self._unknown(language)
    
    def _greeting(self, lang):
        if lang == "sw":
            text = "👋 Habari! Mimi ni MafurikoAI. Naweza kukusaidia na hali ya hewa, hatari za mafuriko, na ushauri wa usalama."
        else:
            text = "👋 Hello! I'm MafurikoAI, your flood safety assistant. I can help with weather updates, flood risks, safe routes, and safety tips."
        return {"text": text, "type": "greeting", "intent": "greeting"}
    
    def _check_flood(self, message, location, lang):
        road = self.predictor.find_road(message)
        weather = self.weather.get_weather(location)
        
        if not road:
            if lang == "sw":
                text = "🗺️ Ungependa nikague barabara gani? Jaribu: 'Je, Thika Road ni salama?'"
            else:
                text = "🗺️ Which road would you like me to check? Try: 'Is Thika Road safe?'"
            return {"text": text, "type": "ask_road", "intent": "flood_check"}
        
        prediction = self.predictor.predict(road, weather, location)
        risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}
        
        if lang == "sw":
            risk_sw = {"low": "CHINI", "medium": "WASTANI", "high": "JUU"}
            text = f"Hatari ya mafuriko kwenye **{road}** ni **{risk_sw[prediction['risk_level']]}** {risk_emoji[prediction['risk_level']]}"
        else:
            text = f"The flood risk on **{road}** is **{prediction['risk_level'].upper()}** {risk_emoji[prediction['risk_level']]}"
        
        return {
            "text": text,
            "type": "prediction",
            "intent": "flood_check",
            "road": road,
            "risk_level": prediction["risk_level"],
            "confidence": prediction["confidence"],
            "alternatives": prediction["alternatives"],
            "safety_message": prediction["safety_message"],
            "weather": weather
        }
    
    def _get_weather_info(self, message, location, lang):
        cities = ["nairobi", "mombasa", "kisumu", "nakuru", "eldoret", "thika", 
                 "machakos", "nyeri", "meru", "kakamega"]
        city = location
        for c in cities:
            if c in message.lower():
                city = c.title()
                break
        
        weather = self.weather.get_weather(city)
        
        if lang == "sw":
            text = f"🌧️ **Hali ya Hewa - {weather['city']}**"
        else:
            text = f"🌧️ **Current Weather in {weather['city']}**"
        
        return {
            "text": text,
            "type": "weather",
            "intent": "weather",
            "weather": weather,
            "is_live": not weather.get("is_mock", False)
        }
    
    def _emergency_info(self, lang):
        if lang == "sw":
            text = """🚨 **MAWASILIANO YA DHARURA - KENYA**

🚔 Polisi: 999 au 112
🏥 Red Cross Kenya: 1199
🚑 Ambulensi: 0722 300 301
🚒 Zima Moto: 999"""
        else:
            text = """🚨 **EMERGENCY CONTACTS - KENYA**

🚔 Police: 999 or 112
🏥 Kenya Red Cross: 1199
🚑 Ambulance: 0722 300 301
🚒 Fire Brigade: 999"""
        return {"text": text, "type": "emergency", "intent": "emergency"}
    
    def _safety_tips(self, lang):
        if lang == "sw":
            text = """🛡️ **VIDOKEZO VYA USALAMA**
✅ Angalia hali ya hewa
✅ Panga njia yako
✅ Usiwahi kuendesha kwenye maji"""
        else:
            text = """🛡️ **FLOOD SAFETY TIPS**
✅ Check weather forecast
✅ Plan your route
✅ Never drive through flooded roads"""
        return {"text": text, "type": "tips", "intent": "tips"}
    
    def _goodbye(self, lang):
        if lang == "sw":
            text = "👋 Kaa salama! Safiri kwa busara! 🇰🇪"
        else:
            text = "👋 Stay safe! Travel smart! 🇰🇪"
        return {"text": text, "type": "goodbye", "intent": "goodbye"}
    
    def _unknown(self, lang):
        if lang == "sw":
            text = "🤔 Sijaelewa. Jaribu: 'Je, Mombasa Road ni salama?'"
        else:
            text = "🤔 I'm not sure I understood. Try: 'Is Mombasa Road safe?'"
        return {"text": text, "type": "unknown", "intent": "unknown"}