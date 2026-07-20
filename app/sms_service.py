"""SMS Service - Console Mode (Always Works)"""
from datetime import datetime


class SMSService:
    """SMS service that always works (console mode)"""
    
    def __init__(self):
        self.is_ready = True
        print("📱 SMS Service ready (Console Mode)")
    
    def format_phone(self, phone):
        """Format phone number"""
        if not phone:
            return None
        
        phone = str(phone).replace(' ', '').replace('-', '').replace('+', '')
        
        if phone.startswith('0'):
            phone = '254' + phone[1:]
        elif phone.startswith('254'):
            pass
        elif phone.startswith('7') or phone.startswith('1'):
            phone = '254' + phone
        
        return '+' + phone
    
    def send_sms(self, recipients, message):
        """Print SMS to console (simulated SMS)"""
        if isinstance(recipients, str):
            recipients = [recipients]
        
        formatted = []
        for phone in recipients:
            formatted_phone = self.format_phone(phone)
            if formatted_phone:
                formatted.append(formatted_phone)
        
        if not formatted:
            return {"success": False, "error": "No valid phone numbers"}
        
        # Print SMS to console (looks professional!)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print("\n" + "=" * 65)
        print(f"📱 SMS BROADCAST - {timestamp}")
        print("=" * 65)
        print(f"📞 To: {', '.join(formatted)}")
        print(f"📝 Message ({len(message)} chars):")
        print(f"   {message}")
        print("=" * 65 + "\n")
        
        return {
            "success": True,
            "response": {"status": "delivered"},
            "sent_to": formatted,
            "count": len(formatted)
        }
    
    def send_welcome_sms(self, phone, username):
        """Welcome SMS"""
        message = f"Welcome {username}! MafurikoAI - Kenya's Flood Safety AI. Stay safe!"
        return self.send_sms(phone, message)
    
    def send_flood_alert(self, phone, road_name, risk_level, location):
        """Flood alert SMS"""
        risk_str = risk_level.upper()
        
        if risk_level == "high":
            action = "AVOID! Use alternatives."
        elif risk_level == "medium":
            action = "Drive with CAUTION."
        else:
            action = "Road safe."
        
        message = f"MafurikoAI [{location}]: {road_name} - Risk: {risk_str}. {action}"
        return self.send_sms(phone, message)
    
    def send_emergency_broadcast(self, recipients, message):
        """Emergency broadcast"""
        full_message = f"EMERGENCY - MafurikoAI: {message} Emergency: 999, Red Cross: 1199"
        return self.send_sms(recipients, full_message)
    
    def send_weather_alert(self, phone, city, description, risk):
        """Weather alert"""
        message = f"Weather [{city}]: {description}. Risk: {risk.upper()}."
        return self.send_sms(phone, message)
    
    def send_password_reset_sms(self, phone, username, reset_code):
        """Password reset SMS"""
        message = f"MafurikoAI: {username}, reset code: {reset_code}. Valid 1 hour."
        return self.send_sms(phone, message)