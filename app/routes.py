"""Flask Routes for MafurikoAI"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from app import db, mail
from app.models import User, Chat, FloodReport
from app.chatbot import Chatbot
from app.predictor import FloodPredictor
from app.weather import WeatherAPI
from datetime import datetime
from flask_mail import Message
import bcrypt
import os

# Create Blueprint
main = Blueprint('main', __name__)

# Initialize services
weather_api = WeatherAPI()
predictor = FloodPredictor()
chatbot = Chatbot(predictor, weather_api)


# ═══════════════════════════════════════════════════════════
# HOME ROUTE
# ═══════════════════════════════════════════════════════════

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('main.admin'))
        return redirect(url_for('main.chat'))
    return redirect(url_for('main.login'))


# ═══════════════════════════════════════════════════════════
# SEO ROUTES
# ═══════════════════════════════════════════════════════════

@main.route('/robots.txt')
def robots():
    """Serve robots.txt for search engines"""
    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    return send_from_directory(static_folder, 'robots.txt')


@main.route('/sitemap.xml')
def sitemap():
    """Serve sitemap.xml for search engines"""
    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    return send_from_directory(static_folder, 'sitemap.xml')


# ═══════════════════════════════════════════════════════════
# AUTHENTICATION ROUTES
# ═══════════════════════════════════════════════════════════

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            login_user(user, remember=True)
            
            if user.role == 'admin':
                return redirect(url_for('main.admin'))
            return redirect(url_for('main.chat'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('main.login'))
    
    return render_template('login.html')


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        location = request.form.get('location', 'Nairobi')
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
            return redirect(url_for('main.signup'))
        
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('Username already taken', 'error')
            return redirect(url_for('main.signup'))
        
        # Create user
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password.decode('utf-8'),
            location=location,
            role='commuter',
            language='en'
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Send welcome email
        try:
            print(f"📧 Attempting to send welcome email to: {email}")
            
            msg = Message(
                subject="🌊 Welcome to MafurikoAI!",
                recipients=[email],
                body=f"""
Hello {username}!

Welcome to MafurikoAI - Kenya's AI-Powered Flood Prediction System! 🇰🇪

Your account has been successfully created:
- Username: {username}
- Email: {email}
- Location: {location}

You can now:
✅ Get real-time flood predictions
✅ Check weather across Kenya
✅ Receive safety recommendations
✅ Chat with our AI assistant

Visit: https://mafuriko-web.onrender.com/login

Stay safe!
The MafurikoAI Team
                """,
                html=f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #4facfe, #00f2fe); padding: 30px; border-radius: 10px; color: white; text-align: center;">
                        <h1>🌊 Welcome to MafurikoAI!</h1>
                        <p style="font-size: 18px;">Kenya's AI-Powered Flood Prediction System 🇰🇪</p>
                    </div>
                    
                    <div style="padding: 30px; background: #f5f5f5; border-radius: 10px; margin-top: 20px;">
                        <h2>Hello {username}! 👋</h2>
                        <p>Your account has been successfully created:</p>
                        <ul>
                            <li><strong>Username:</strong> {username}</li>
                            <li><strong>Email:</strong> {email}</li>
                            <li><strong>Location:</strong> {location}</li>
                        </ul>
                        
                        <h3>You can now:</h3>
                        <ul style="line-height: 2;">
                            <li>✅ Get real-time flood predictions</li>
                            <li>✅ Check weather across Kenya</li>
                            <li>✅ Receive safety recommendations</li>
                            <li>✅ Chat with our AI assistant</li>
                        </ul>
                        
                        <div style="text-align: center; margin-top: 30px;">
                            <a href="https://mafuriko-web.onrender.com/login" 
                               style="background: #4facfe; color: white; padding: 15px 30px; 
                                      text-decoration: none; border-radius: 5px; display: inline-block;">
                                Login to MafurikoAI
                            </a>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 20px; color: #666;">
                        <p>Stay safe!</p>
                        <p><strong>The MafurikoAI Team</strong></p>
                    </div>
                </div>
                """
            )
            
            mail.send(msg)
            print(f"✅ Welcome email sent to {email}")
            
        except Exception as e:
            print(f"❌ Email error: {str(e)}")
        
        flash('Account created successfully! Please check your email.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('signup.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


# ═══════════════════════════════════════════════════════════
# PASSWORD RESET ROUTES
# ═══════════════════════════════════════════════════════════

@main.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            try:
                # Send reset email
                msg = Message(
                    subject="🔐 Reset Your MafurikoAI Password",
                    recipients=[email],
                    html=f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2>Password Reset Request</h2>
                        <p>Hi {user.username},</p>
                        <p>Click the link below to reset your password:</p>
                        <a href="https://mafuriko-web.onrender.com/reset-password?email={email}"
                           style="background: #4facfe; color: white; padding: 10px 20px; 
                                  text-decoration: none; border-radius: 5px;">
                            Reset Password
                        </a>
                        <p>If you didn't request this, please ignore this email.</p>
                    </div>
                    """
                )
                mail.send(msg)
                flash('Password reset link sent to your email!', 'success')
            except Exception as e:
                print(f"❌ Email error: {str(e)}")
                flash('Error sending email. Please try again.', 'error')
        else:
            flash('Email not found', 'error')
        
        return redirect(url_for('main.login'))
    
    return render_template('forgot_password.html')


# ═══════════════════════════════════════════════════════════
# CHATBOT ROUTES
# ═══════════════════════════════════════════════════════════

@main.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=current_user)


@main.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    data = request.get_json()
    message = data.get('message', '')
    language = data.get('language', 'en')
    
    response = chatbot.get_response(message, current_user.location, language)
    
    # Save to database
    chat_entry = Chat(
        user_id=current_user.id,
        message=message,
        response=response.get('text', ''),
        intent=response.get('intent', '')
    )
    db.session.add(chat_entry)
    db.session.commit()
    
    return jsonify(response)


# ═══════════════════════════════════════════════════════════
# MAP ROUTES
# ═══════════════════════════════════════════════════════════

@main.route('/map')
@login_required
def map_view():
    return render_template('map.html', user=current_user)


@main.route('/api/map/data')
@login_required
def map_data():
    import random
    
    kenya_cities = [
        {"name": "Nairobi", "lat": -1.2921, "lng": 36.8219, "county": "Nairobi"},
        {"name": "Mombasa", "lat": -4.0435, "lng": 39.6682, "county": "Mombasa"},
        {"name": "Kisumu", "lat": -0.0917, "lng": 34.7680, "county": "Kisumu"},
        {"name": "Nakuru", "lat": -0.3031, "lng": 36.0800, "county": "Nakuru"},
        {"name": "Eldoret", "lat": 0.5143, "lng": 35.2698, "county": "Uasin Gishu"},
        {"name": "Thika", "lat": -1.0332, "lng": 37.0693, "county": "Kiambu"},
        {"name": "Machakos", "lat": -1.5177, "lng": 37.2634, "county": "Machakos"},
        {"name": "Nyeri", "lat": -0.4204, "lng": 36.9483, "county": "Nyeri"},
        {"name": "Meru", "lat": 0.0470, "lng": 37.6559, "county": "Meru"},
        {"name": "Kakamega", "lat": 0.2827, "lng": 34.7519, "county": "Kakamega"},
    ]
    
    map_data_result = []
    for city in kenya_cities:
        rainfall = random.uniform(0, 100)
        risk_level = "high" if rainfall > 60 else "medium" if rainfall > 30 else "low"
        
        map_data_result.append({
            "name": city["name"],
            "county": city["county"],
            "lat": city["lat"],
            "lng": city["lng"],
            "risk_level": risk_level,
            "confidence": random.uniform(80, 95),
            "weather_data": {
                "rainfall_mm": rainfall,
                "temperature_c": random.uniform(18, 30),
                "humidity_percent": random.uniform(50, 90),
                "description": "Partly cloudy"
            }
        })
    
    return jsonify(map_data_result)


# ═══════════════════════════════════════════════════════════
# ANALYTICS ROUTES
# ═══════════════════════════════════════════════════════════

@main.route('/analytics')
@login_required
def analytics():
    if current_user.role == 'admin':
        return render_template('admin_analytics.html', user=current_user)
    return render_template('user_analytics.html', user=current_user)


# ═══════════════════════════════════════════════════════════
# PROFILE ROUTES
# ═══════════════════════════════════════════════════════════

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@main.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    current_user.email = request.form.get('email', current_user.email)
    current_user.location = request.form.get('location', current_user.location)
    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('main.profile'))


# ═══════════════════════════════════════════════════════════
# ADMIN ROUTES
# ═══════════════════════════════════════════════════════════

@main.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        return redirect(url_for('main.chat'))
    
    users = User.query.all()
    chats = Chat.query.order_by(Chat.timestamp.desc()).limit(50).all()
    
    return render_template('admin.html', 
                         user=current_user,
                         users=users,
                         chats=chats)


@main.route('/admin/sms')
@login_required
def admin_sms():
    if current_user.role != 'admin':
        return redirect(url_for('main.chat'))
    return render_template('admin_sms.html', user=current_user)


# ═══════════════════════════════════════════════════════════
# WEATHER API ROUTES
# ═══════════════════════════════════════════════════════════

@main.route('/api/weather/<city>')
def get_weather(city):
    weather = weather_api.get_weather(city)
    return jsonify(weather)