"""Flask Routes for MafurikoAI - Complete Version"""
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

main = Blueprint('main', __name__)

weather_api = WeatherAPI()
predictor = FloodPredictor()
chatbot = Chatbot(predictor, weather_api)


@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('main.admin'))
        return redirect(url_for('main.chat'))
    return redirect(url_for('main.login'))


@main.route('/robots.txt')
def robots():
    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    return send_from_directory(static_folder, 'robots.txt')


@main.route('/sitemap.xml')
def sitemap():
    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    return send_from_directory(static_folder, 'sitemap.xml')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        print(f"🔐 Login attempt: username='{username}'")
        
        if not username or not password:
            flash('Please enter username and password', 'error')
            return redirect(url_for('main.login'))
        
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            print(f"❌ User not found: {username}")
            flash('Invalid username or password', 'error')
            return redirect(url_for('main.login'))
        
        print(f"✅ User found: {user.username} (role: {user.role})")
        
        try:
            if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                print(f"✅ Password correct for {user.username}")
                login_user(user, remember=True)
                
                if user.role == 'admin':
                    return redirect(url_for('main.admin'))
                return redirect(url_for('main.chat'))
            else:
                print(f"❌ Wrong password for {user.username}")
                flash('Invalid username or password', 'error')
                return redirect(url_for('main.login'))
        except Exception as e:
            print(f"❌ Password check error: {str(e)}")
            flash('Login error. Please try again.', 'error')
            return redirect(url_for('main.login'))
    
    return render_template('login.html')


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        location = request.form.get('location', 'Nairobi')
        
        print(f"📝 Signup attempt: username='{username}', email='{email}'")
        
        if not username or not email or not password:
            flash('Please fill all required fields', 'error')
            return redirect(url_for('main.signup'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return redirect(url_for('main.signup'))
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"❌ Username already exists: {username}")
            flash('Username already taken', 'error')
            return redirect(url_for('main.signup'))
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            print(f"❌ Email already exists: {email}")
            flash('Email already registered', 'error')
            return redirect(url_for('main.signup'))
        
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            new_user = User(
                username=username,
                email=email,
                phone=phone,
                password_hash=hashed_password.decode('utf-8'),
                location=location,
                role='commuter',
                language='en'
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            print(f"✅ User created: {username} (ID: {new_user.id})")
            
            try:
                msg = Message(
                    subject="Welcome to MafurikoAI!",
                    recipients=[email],
                    body=f"Hello {username}!\n\nWelcome to MafurikoAI!\n\nStay safe!\nThe MafurikoAI Team"
                )
                mail.send(msg)
                print(f"✅ Welcome email sent to {email}")
            except Exception as e:
                print(f"⚠️ Email error (non-critical): {str(e)}")
            
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('main.login'))
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Database error: {str(e)}")
            flash('Error creating account. Please try again.', 'error')
            return redirect(url_for('main.signup'))
    
    return render_template('signup.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


@main.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()
        
        if user:
            try:
                msg = Message(
                    subject="Reset Your MafurikoAI Password",
                    recipients=[email],
                    body=f"Hi {user.username},\n\nClick here to reset: https://mafuriko-web.onrender.com/login\n\nMafurikoAI Team"
                )
                mail.send(msg)
                flash('Password reset link sent to your email!', 'success')
            except Exception as e:
                print(f"❌ Email error: {str(e)}")
                flash('Error sending email.', 'error')
        else:
            flash('Email not found', 'error')
        
        return redirect(url_for('main.login'))
    
    return render_template('forgot_password.html')


@main.route('/chat')
@login_required
def chat():
    if current_user.role == 'admin':
        return redirect(url_for('main.admin'))
    return render_template('chat.html', user=current_user)


@main.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    data = request.get_json()
    message = data.get('message', '')
    language = data.get('language', 'en')
    
    response = chatbot.get_response(message, current_user.location, language)
    
    try:
        chat_entry = Chat(
            user_id=current_user.id,
            message=message,
            response=response.get('text', ''),
            intent=response.get('intent', '')
        )
        db.session.add(chat_entry)
        db.session.commit()
    except Exception as e:
        print(f"Chat save error: {str(e)}")
    
    return jsonify(response)


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
    
    result = []
    for city in kenya_cities:
        rainfall = random.uniform(0, 100)
        risk = "high" if rainfall > 60 else "medium" if rainfall > 30 else "low"
        
        result.append({
            "name": city["name"],
            "county": city["county"],
            "lat": city["lat"],
            "lng": city["lng"],
            "risk_level": risk,
            "confidence": round(random.uniform(80, 95), 1),
            "temperature": round(random.uniform(18, 30), 1),
            "humidity": round(random.uniform(50, 90), 1),
            "rainfall": round(rainfall, 1),
            "description": "Partly Cloudy"
        })
    
    return jsonify(result)


@main.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html', user=current_user)


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
    flash('Profile updated!', 'success')
    return redirect(url_for('main.profile'))


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


@main.route('/api/weather/<city>')
def get_weather(city):
    weather = weather_api.get_weather(city)
    return jsonify(weather)


@main.route('/debug/users')
def debug_users():
    users = User.query.all()
    
    html = "<h1>Database Users</h1>"
    html += f"<p><strong>Total: {len(users)}</strong></p>"
    
    if not users:
        html += "<p style='color:red;'>NO USERS!</p>"
    else:
        for user in users:
            html += f"<div style='border:1px solid #ccc; padding:10px; margin:10px;'>"
            html += f"<strong>ID:</strong> {user.id}<br>"
            html += f"<strong>Username:</strong> {user.username}<br>"
            html += f"<strong>Email:</strong> {user.email}<br>"
            html += f"<strong>Role:</strong> {user.role}<br>"
            html += f"<strong>Location:</strong> {user.location}<br>"
            html += f"</div>"
    
    return html