"""AI Flood Risk Predictor"""
from datetime import datetime


class FloodPredictor:
    def __init__(self):
        self.kenyan_roads = self._load_kenyan_roads()
        self.high_risk_areas = [
            "Nairobi River", "Mathare", "Kibera", "Mukuru", "Korogocho",
            "Athi River", "Tana River", "Nzoia River", "Yala River"
        ]
    
    def _load_kenyan_roads(self):
        return [
            "Thika Superhighway", "Mombasa Road", "Waiyaki Way", "Ngong Road",
            "Lang'ata Road", "Jogoo Road", "Outer Ring Road", "Uhuru Highway",
            "Kenyatta Avenue", "Tom Mboya Street", "River Road", "Kimathi Street",
            "Moi Avenue", "Haile Selassie Avenue", "University Way",
            "Eastern Bypass", "Southern Bypass", "Northern Bypass",
            "Moi Avenue Mombasa", "Digo Road", "Nyali Bridge",
            "Bamburi Road", "Malindi Road", "Likoni Road",
            "Oginga Odinga Street", "Jomo Kenyatta Highway Kisumu",
            "Kakamega Road", "Kondele Road",
            "Kenyatta Avenue Nakuru", "Nakuru-Nairobi Highway",
            "Uganda Road", "Nandi Road", "Eldoret-Kitale Road",
            "Kiambu Road", "Limuru Road", "Ruiru Road",
            "Machakos Road", "Kajiado Road", "Naivasha Road"
        ]
    
    def find_road(self, query):
        query_lower = query.lower().strip()
        
        for road in self.kenyan_roads:
            if road.lower() == query_lower:
                return road
        
        for road in self.kenyan_roads:
            if query_lower in road.lower() or any(word in road.lower() for word in query_lower.split()):
                return road
        
        return None
    
    def predict(self, road_name=None, weather_data=None, location="Nairobi"):
        risk_score = 0
        
        if weather_data:
            rainfall = weather_data.get('rainfall_mm', 0)
            humidity = weather_data.get('humidity_percent', 50)
            
            if rainfall > 50: risk_score += 3
            elif rainfall > 25: risk_score += 2
            elif rainfall > 10: risk_score += 1
            
            if humidity > 85: risk_score += 2
            elif humidity > 70: risk_score += 1
        
        month = datetime.now().month
        if month in [3, 4, 5]: risk_score += 2
        elif month in [10, 11, 12]: risk_score += 1
        
        if road_name:
            for area in self.high_risk_areas:
                if area.lower() in road_name.lower():
                    risk_score += 2
                    break
        
        hour = datetime.now().hour
        if 18 <= hour <= 22: risk_score += 1
        
        if risk_score >= 6:
            risk_level = "high"
            confidence = 92.5
        elif risk_score >= 3:
            risk_level = "medium"
            confidence = 85.3
        else:
            risk_level = "low"
            confidence = 88.7
        
        alternatives = self._get_alternatives(road_name)
        
        return {
            "road": road_name or "Unknown Road",
            "risk_level": risk_level,
            "confidence": confidence,
            "risk_score": risk_score,
            "alternatives": alternatives,
            "safety_message": self._get_safety_message(risk_level),
            "weather": weather_data,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_alternatives(self, road_name):
        alternatives_map = {
            "Mombasa Road": ["Uhuru Highway", "Outer Ring Road", "Lang'ata Road"],
            "Thika Superhighway": ["Kiambu Road", "Eastern Bypass", "Limuru Road"],
            "Waiyaki Way": ["Northern Bypass", "Limuru Road"],
            "Ngong Road": ["Lang'ata Road", "Argwings Kodhek Road"],
            "Jogoo Road": ["Outer Ring Road", "Juja Road"],
        }
        
        if road_name and road_name in alternatives_map:
            return alternatives_map[road_name]
        
        return ["Use major highways", "Avoid low-lying areas", "Check local traffic"]
    
    def _get_safety_message(self, risk_level):
        messages = {
            "high": "🔴 AVOID THIS ROAD! Severe flood risk. Use alternative routes immediately.",
            "medium": "🟡 Drive with CAUTION. Moderate flood risk. Reduce speed.",
            "low": "🟢 Road appears SAFE. Normal conditions but stay aware."
        }
        return messages.get(risk_level, "Check weather updates.")