"""Email Service for MafurikoAI"""
from flask import current_app, render_template_string
from flask_mail import Message
from threading import Thread


def send_async_email(app, msg, mail):
    """Send email asynchronously"""
    with app.app_context():
        try:
            mail.send(msg)
            print(f"✅ Email sent to {msg.recipients}")
        except Exception as e:
            print(f"❌ Email error: {e}")


def send_email(subject, recipients, html_body, mail):
    """Send email with HTML body"""
    from flask import current_app
    
    try:
        msg = Message(
            subject=f"🌧️ MafurikoAI - {subject}",
            recipients=recipients if isinstance(recipients, list) else [recipients],
            html=html_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Send asynchronously (doesn't block user)
        app = current_app._get_current_object()
        Thread(target=send_async_email, args=(app, msg, mail)).start()
        return True
    except Exception as e:
        print(f"❌ Email setup error: {e}")
        return False


# ══════════════════════════════════════════════════════
# EMAIL TEMPLATES
# ══════════════════════════════════════════════════════

def welcome_email_template(username, location):
    """Beautiful welcome email"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #1e3c72, #2a5298, #4facfe); padding: 40px 30px; text-align: center; color: white; }}
            .logo {{ font-size: 4rem; margin-bottom: 10px; }}
            .header h1 {{ margin: 0; font-size: 2rem; font-weight: 700; }}
            .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
            .content {{ padding: 40px 30px; color: #2c3e50; }}
            .content h2 {{ color: #1e3c72; margin-top: 0; }}
            .content p {{ line-height: 1.7; color: #555; }}
            .features {{ background: #f0f4f8; padding: 25px; border-radius: 12px; margin: 25px 0; }}
            .feature {{ display: flex; align-items: center; padding: 10px 0; }}
            .feature-icon {{ font-size: 2rem; margin-right: 15px; }}
            .button {{ display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; text-decoration: none; border-radius: 10px; font-weight: 600; margin: 20px 0; }}
            .footer {{ background: #2c3e50; color: white; padding: 25px; text-align: center; font-size: 0.9rem; }}
            .footer a {{ color: #4facfe; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🌧️</div>
                <h1>Welcome to MafurikoAI!</h1>
                <p>Kenya's AI Flood Safety Assistant</p>
            </div>
            
            <div class="content">
                <h2>Habari {username}! 👋</h2>
                
                <p>Thank you for joining <strong>MafurikoAI</strong>! We're excited to help you stay safe from floods across Kenya.</p>
                
                <p>Your account has been successfully created for <strong>{location}</strong>.</p>
                
                <div class="features">
                    <h3 style="margin-top:0; color:#1e3c72;">🎯 What You Can Do:</h3>
                    
                    <div class="feature">
                        <span class="feature-icon">💬</span>
                        <div>
                            <strong>AI Chatbot</strong><br>
                            <small style="color:#666;">Ask about weather, floods, safe routes</small>
                        </div>
                    </div>
                    
                    <div class="feature">
                        <span class="feature-icon">🗺️</span>
                        <div>
                            <strong>Kenya Flood Map</strong><br>
                            <small style="color:#666;">Real-time risk zones across 20+ cities</small>
                        </div>
                    </div>
                    
                    <div class="feature">
                        <span class="feature-icon">🌧️</span>
                        <div>
                            <strong>Weather Updates</strong><br>
                            <small style="color:#666;">Live weather for your location</small>
                        </div>
                    </div>
                    
                    <div class="feature">
                        <span class="feature-icon">🇰🇪</span>
                        <div>
                            <strong>English + Kiswahili</strong><br>
                            <small style="color:#666;">Chat in your preferred language</small>
                        </div>
                    </div>
                </div>
                
                <div style="text-align:center;">
                    <a href="http://localhost:5000/login" class="button">
                        🚀 Get Started Now
                    </a>
                </div>
                
                <p style="margin-top:30px; padding-top:20px; border-top:1px solid #eee; color:#666; font-size:0.9rem;">
                    <strong>Safety First:</strong> Always check MafurikoAI before traveling during rainy season. 
                    Emergency numbers: Police 999 | Red Cross 1199
                </p>
            </div>
            
            <div class="footer">
                <p style="margin:0;">© 2025 <strong>MafurikoAI</strong> | Kenya 🇰🇪</p>
                <p style="margin:10px 0 0 0; opacity:0.7;">
                    Stay safe. Travel smart. Kaa salama.
                </p>
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
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #f5576c, #f093fb); padding: 40px 30px; text-align: center; color: white; }}
            .logo {{ font-size: 4rem; margin-bottom: 10px; }}
            .header h1 {{ margin: 0; font-size: 2rem; }}
            .content {{ padding: 40px 30px; color: #2c3e50; }}
            .content p {{ line-height: 1.7; color: #555; }}
            .button {{ display: inline-block; padding: 15px 40px; background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; text-decoration: none; border-radius: 10px; font-weight: 600; margin: 20px 0; }}
            .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            .footer {{ background: #2c3e50; color: white; padding: 25px; text-align: center; font-size: 0.9rem; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">🔐</div>
                <h1>Password Reset Request</h1>
            </div>
            
            <div class="content">
                <h2 style="color:#1e3c72;">Hi {username},</h2>
                
                <p>We received a request to reset your MafurikoAI password.</p>
                
                <p>Click the button below to create a new password:</p>
                
                <div style="text-align:center;">
                    <a href="{reset_link}" class="button">
                        🔑 Reset My Password
                    </a>
                </div>
                
                <div class="warning">
                    <strong>⏰ This link expires in 1 hour</strong><br>
                    <small>If you didn't request this, ignore this email.</small>
                </div>
                
                <p style="margin-top:30px; color:#666; font-size:0.9rem;">
                    Or copy and paste this link into your browser:<br>
                    <a href="{reset_link}" style="color:#4facfe; word-break:break-all;">{reset_link}</a>
                </p>
                
                <p style="margin-top:20px; padding-top:20px; border-top:1px solid #eee; color:#666; font-size:0.85rem;">
                    <strong>🔒 Security tip:</strong> Never share this link with anyone. 
                    MafurikoAI will never ask for your password via email.
                </p>
            </div>
            
            <div class="footer">
                <p style="margin:0;">© 2025 <strong>MafurikoAI</strong> | Kenya 🇰🇪</p>
                <p style="margin:10px 0 0 0; opacity:0.7;">
                    Stay safe. Travel smart.
                </p>
            </div>
        </div>
    </body>
    </html>
    """


def password_changed_email_template(username):
    """Confirmation email after password change"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 15px; overflow: hidden; }}
            .header {{ background: linear-gradient(135deg, #00b09b, #96c93d); padding: 40px 30px; text-align: center; color: white; }}
            .logo {{ font-size: 4rem; }}
            .content {{ padding: 40px 30px; color: #2c3e50; }}
            .footer {{ background: #2c3e50; color: white; padding: 25px; text-align: center; font-size: 0.9rem; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">✅</div>
                <h1>Password Changed Successfully</h1>
            </div>
            <div class="content">
                <h2>Hi {username},</h2>
                <p>Your MafurikoAI password was successfully changed.</p>
                <p style="background:#e8f5e9; padding:15px; border-radius:8px; border-left:4px solid #4caf50;">
                    <strong>✅ Confirmation:</strong> Your account is now secured with your new password.
                </p>
                <p style="color:#666; margin-top:20px;">
                    If you didn't make this change, please contact us immediately.
                </p>
            </div>
            <div class="footer">
                <p>© 2025 <strong>MafurikoAI</strong> | Kenya 🇰🇪</p>
            </div>
        </div>
    </body>
    </html>
    """