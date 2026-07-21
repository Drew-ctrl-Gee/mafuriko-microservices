"""Email Service for MafurikoAI - With Background Sending"""
from threading import Thread


def send_async_email(app, msg, mail_instance):
    """Send email in background thread"""
    with app.app_context():
        try:
            mail_instance.send(msg)
            print(f"✅ Email sent to {msg.recipients}")
        except Exception as e:
            print(f"❌ Background email error: {str(e)}")


def send_email_background(subject, recipients, html_content):
    """Send email without blocking the page"""
    try:
        from flask import current_app
        from flask_mail import Message
        from app import mail
        
        app = current_app._get_current_object()
        
        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            html=html_content
        )
        
        thread = Thread(target=send_async_email, args=(app, msg, mail))
        thread.start()
        
        print(f"📧 Email queued for {recipients}")
        return True
        
    except Exception as e:
        print(f"❌ Email setup error: {str(e)}")
        return False


def welcome_email_template(username, location):
    """Beautiful welcome email"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.1);">
            
            <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #4facfe 100%); padding: 50px 30px; text-align: center; color: white;">
                <div style="font-size: 60px; margin-bottom: 15px;">🌧️</div>
                <h1 style="margin: 0; font-size: 28px; font-weight: 700;">Welcome to MafurikoAI!</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 16px;">Kenya's AI Flood Safety Assistant</p>
            </div>
            
            <div style="padding: 40px 30px; color: #2c3e50;">
                <h2 style="color: #1e3c72; margin-top: 0; font-size: 22px;">Habari {username}! 👋</h2>
                
                <p style="line-height: 1.7; color: #555; font-size: 15px;">
                    Thank you for joining <strong>MafurikoAI</strong>! We're excited to help you stay safe from floods across Kenya.
                </p>
                
                <p style="line-height: 1.7; color: #555; font-size: 15px;">
                    Your account has been successfully created for <strong>{location}</strong>.
                </p>
                
                <div style="background: #f8f9fa; padding: 25px; border-radius: 12px; margin: 25px 0; border-left: 4px solid #4facfe;">
                    <h3 style="margin-top: 0; color: #1e3c72; font-size: 18px;">🎯 What You Can Do:</h3>
                    
                    <div style="display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #eee;">
                        <span style="font-size: 28px; margin-right: 15px;">💬</span>
                        <div>
                            <strong style="color: #333;">AI Chatbot</strong><br>
                            <small style="color: #888;">Ask about weather, floods, safe routes</small>
                        </div>
                    </div>
                    
                    <div style="display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #eee;">
                        <span style="font-size: 28px; margin-right: 15px;">🗺️</span>
                        <div>
                            <strong style="color: #333;">Kenya Flood Map</strong><br>
                            <small style="color: #888;">Real-time risk zones across 20+ cities</small>
                        </div>
                    </div>
                    
                    <div style="display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #eee;">
                        <span style="font-size: 28px; margin-right: 15px;">🌧️</span>
                        <div>
                            <strong style="color: #333;">Weather Updates</strong><br>
                            <small style="color: #888;">Live weather for your location</small>
                        </div>
                    </div>
                    
                    <div style="display: flex; align-items: center; padding: 12px 0;">
                        <span style="font-size: 28px; margin-right: 15px;">🇰🇪</span>
                        <div>
                            <strong style="color: #333;">English + Kiswahili</strong><br>
                            <small style="color: #888;">Chat in your preferred language</small>
                        </div>
                    </div>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://mafuriko-web.onrender.com/login" 
                       style="display: inline-block; padding: 16px 40px; background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; text-decoration: none; border-radius: 50px; font-weight: 600; font-size: 16px; box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);">
                        🚀 Get Started Now
                    </a>
                </div>
                
                <div style="border-top: 1px solid #eee; padding-top: 20px; margin-top: 20px;">
                    <p style="color: #666; font-size: 13px; line-height: 1.6;">
                        <strong>Safety First:</strong> Always check MafurikoAI before traveling during rainy season.
                        Emergency numbers: Police 999 | Red Cross 1199
                    </p>
                </div>
            </div>
            
            <div style="background: #2c3e50; color: white; padding: 25px; text-align: center;">
                <p style="margin: 0; font-size: 14px;">&copy; 2025 <strong>MafurikoAI</strong> | Kenya 🇰🇪</p>
                <p style="margin: 10px 0 0 0; opacity: 0.7; font-size: 13px;">Stay safe. Travel smart. Kaa salama.</p>
            </div>
        </div>
    </body>
    </html>
    """


def admin_created_user_email_template(username, password, role, location):
    """Email when admin creates a user account"""
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; background: #f0f2f5; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #1e3c72, #4facfe); padding: 40px; text-align: center; color: white;">
                <div style="font-size: 50px;">🌧️</div>
                <h1 style="margin: 15px 0 0 0;">Welcome to MafurikoAI!</h1>
                <p style="opacity: 0.9;">Your account has been created by an administrator</p>
            </div>
            <div style="padding: 30px;">
                <h2>Habari {username}! 👋</h2>
                <p>An admin has created your MafurikoAI account.</p>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1e3c72;">Your Login Details:</h3>
                    <p><strong>Username:</strong> {username}</p>
                    <p><strong>Password:</strong> {password}</p>
                    <p><strong>Role:</strong> {role}</p>
                    <p><strong>Location:</strong> {location}</p>
                </div>
                <div style="background: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <strong>⚠️ Important:</strong> Please change your password after your first login!
                </div>
                <div style="text-align: center; margin: 25px 0;">
                    <a href="https://mafuriko-web.onrender.com/login" style="padding: 15px 35px; background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; text-decoration: none; border-radius: 50px; font-weight: 600;">
                        🚀 Login Now
                    </a>
                </div>
            </div>
            <div style="background: #2c3e50; color: white; padding: 20px; text-align: center;">
                <p style="margin: 0;">&copy; 2025 MafurikoAI | Kenya 🇰🇪</p>
                <p style="margin: 5px 0 0 0; opacity: 0.7; font-size: 13px;">Stay safe. Travel smart. Kaa salama.</p>
            </div>
        </div>
    </body>
    </html>
    """


def password_reset_email_template(username, reset_link):
    """Password reset email"""
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; background: #f0f2f5; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #f5576c, #f093fb); padding: 40px; text-align: center; color: white;">
                <div style="font-size: 50px;">🔐</div>
                <h1 style="margin: 15px 0 0 0;">Password Reset</h1>
            </div>
            <div style="padding: 30px;">
                <h2>Hi {username},</h2>
                <p>Click below to reset your password:</p>
                <div style="text-align: center; margin: 25px 0;">
                    <a href="{reset_link}" style="padding: 15px 35px; background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; text-decoration: none; border-radius: 50px; font-weight: 600;">
                        🔑 Reset My Password
                    </a>
                </div>
                <p style="color: #888; font-size: 13px;">This link expires in 1 hour.</p>
            </div>
            <div style="background: #2c3e50; color: white; padding: 20px; text-align: center;">
                <p style="margin: 0;">&copy; 2025 MafurikoAI | Kenya 🇰🇪</p>
            </div>
        </div>
    </body>
    </html>
    """


def password_changed_email_template(username):
    """Password changed confirmation"""
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; background: #f0f2f5; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #00b09b, #96c93d); padding: 40px; text-align: center; color: white;">
                <div style="font-size: 50px;">✅</div>
                <h1 style="margin: 15px 0 0 0;">Password Changed</h1>
            </div>
            <div style="padding: 30px;">
                <h2>Hi {username},</h2>
                <p>Your password was successfully changed.</p>
                <p style="color: #888;">If you didn't make this change, contact us immediately.</p>
            </div>
            <div style="background: #2c3e50; color: white; padding: 20px; text-align: center;">
                <p style="margin: 0;">&copy; 2025 MafurikoAI | Kenya 🇰🇪</p>
            </div>
        </div>
    </body>
    </html>
    """