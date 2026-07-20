"""Flask Routes for MafurikoAI"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Chat, FloodReport
from app.chatbot import Chatbot
from app.predictor import FloodPredictor
from app.weather import WeatherAPI
from app.sms_service import SMSService
from datetime import datetime
import bcrypt

main = Blueprint('main', __name__)

# Initialize services
weather_api = WeatherAPI()
predictor = FloodPredictor()
chatbot = Chatbot(predictor, weather_api)
sms_service = SMSService()


# ═══════════════════════════════════════════════════════════
# AUTHENTICATION ROUTES
# ═══════════════════════════════════════════════════════════

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('main.admin'))
        return redirect(url_for('main.chat'))
    return redirect(url_for('main.login'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=True)
            flash('Welcome back!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone', '')
        password = request.form.get('password')
        location = request.form.get('location', 'Nairobi')
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return render_template('signup.html')
        
        pass_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        new_user = User(
            username=username,
            email=email,
            phone=phone,
            password_hash=pass_hash.decode('utf-8'),
            role='commuter',
            location=location,
            language='en'
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Send welcome email
        try:
            from app import mail
            from app.email_service import send_email, welcome_email_template
            
            html = welcome_email_template(username, location)
            send_email(
                subject="Welcome to MafurikoAI! 🌧️",
                recipients=email,
                html_body=html,
                mail=mail
            )
        except Exception as e:
            print(f"Welcome email error: {e}")
        
        # Send welcome SMS
        try:
            if phone:
                sms_service.send_welcome_sms(phone, username)
        except Exception as e:
            print(f"Welcome SMS error: {e}")
        
        flash('Account created! Check your email/phone. Please login.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('signup.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))


# ═══════════════════════════════════════════════════════════
# PASSWORD RESET ROUTES
# ═══════════════════════════════════════════════════════════

@main.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')
        
        user = User.query.filter(
            (User.email == email) | (User.phone == phone)
        ).first()
        
        if user:
            import secrets
            from datetime import timedelta
            from app.models import PasswordReset
            
            token = secrets.token_urlsafe(32)
            
            reset = PasswordReset(
                user_id=user.id,
                token=token,
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            db.session.add(reset)
            db.session.commit()
            
            reset_link = url_for('main.reset_password', token=token, _external=True)
            
            # Send email
            try:
                from app import mail
                from app.email_service import send_email, password_reset_email_template
                
                html = password_reset_email_template(user.username, reset_link)
                send_email(
                    subject="Password Reset Request 🔐",
                    recipients=user.email,
                    html_body=html,
                    mail=mail
                )
                
                flash(f'Reset link sent to {user.email}!', 'success')
            except Exception as e:
                print(f"Reset email error: {e}")
            
            return render_template('forgot_password.html', 
                                 success=True, 
                                 reset_link=reset_link,
                                 user_email=user.email)
        else:
            flash('No account found with this email or phone number', 'danger')
    
    return render_template('forgot_password.html', success=False)


@main.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    from app.models import PasswordReset
    
    reset = PasswordReset.query.filter_by(token=token, used=False).first()
    
    if not reset:
        flash('Invalid or expired reset link', 'danger')
        return redirect(url_for('main.forgot_password'))
    
    if reset.expires_at < datetime.utcnow():
        flash('Reset link expired. Request a new one.', 'danger')
        return redirect(url_for('main.forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('reset_password.html', token=token)
        
        if len(new_password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('reset_password.html', token=token)
        
        user = User.query.get(reset.user_id)
        new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.password_hash = new_hash.decode('utf-8')
        
        reset.used = True
        db.session.commit()
        
        flash('Password reset successfully! Please login.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('reset_password.html', token=token)


# ═══════════════════════════════════════════════════════════
# CHAT ROUTES
# ═══════════════════════════════════════════════════════════

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
    message = data.get('message', '').strip()
    language = data.get('language', 'auto')
    
    if not message:
        return jsonify({"error": "Empty message"}), 400
    
    response = chatbot.get_response(message, current_user.location, language)
    
    chat_entry = Chat(
        user_id=current_user.id,
        message=message,
        response=response.get('text', ''),
        intent=response.get('intent', ''),
        road_queried=response.get('road', ''),
        risk_level=response.get('risk_level', ''),
        location=current_user.location
    )
    db.session.add(chat_entry)
    db.session.commit()
    
    return jsonify(response)


@main.route('/api/weather')
@login_required
def api_weather():
    city = request.args.get('city', current_user.location)
    weather = weather_api.get_weather(city)
    return jsonify(weather)


# ═══════════════════════════════════════════════════════════
# PROFILE ROUTES
# ═══════════════════════════════════════════════════════════

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@main.route('/api/profile/update', methods=['POST'])
@login_required
def api_update_profile():
    data = request.get_json()
    
    if 'location' in data and data['location']:
        current_user.location = data['location']
    
    if 'phone' in data:
        current_user.phone = data['phone']
    
    if 'language' in data:
        current_user.language = data['language']
    
    if 'email' in data and data['email'] != current_user.email:
        existing = User.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({"success": False, "message": "Email already taken"}), 400
        current_user.email = data['email']
    
    try:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Profile updated successfully!",
            "user": current_user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@main.route('/api/profile/change-password', methods=['POST'])
@login_required
def api_change_password():
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({"success": False, "message": "All fields required"}), 400
    
    if len(new_password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400
    
    if not bcrypt.checkpw(current_password.encode('utf-8'), current_user.password_hash.encode('utf-8')):
        return jsonify({"success": False, "message": "Current password is incorrect"}), 400
    
    new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    current_user.password_hash = new_hash.decode('utf-8')
    
    try:
        db.session.commit()
        
        # Send confirmation email
        try:
            from app import mail
            from app.email_service import send_email, password_changed_email_template
            
            html = password_changed_email_template(current_user.username)
            send_email(
                subject="Password Changed ✅",
                recipients=current_user.email,
                html_body=html,
                mail=mail
            )
        except Exception as e:
            print(f"Email error: {e}")
        
        return jsonify({"success": True, "message": "Password changed successfully!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ═══════════════════════════════════════════════════════════
# MAP ROUTES
# ═══════════════════════════════════════════════════════════

@main.route('/map')
@login_required
def map_view():
    return render_template('map.html', user=current_user)


@main.route('/api/map/data')
@login_required
def api_map_data():
    import random
    
    kenya_cities = [
        {"name": "Nairobi", "lat": -1.2921, "lng": 36.8219, "county": "Nairobi"},
        {"name": "Mombasa", "lat": -4.0435, "lng": 39.6682, "county": "Mombasa"},
        {"name": "Kisumu", "lat": -0.1022, "lng": 34.7617, "county": "Kisumu"},
        {"name": "Nakuru", "lat": -0.3031, "lng": 36.0800, "county": "Nakuru"},
        {"name": "Eldoret", "lat": 0.5143, "lng": 35.2698, "county": "Uasin Gishu"},
        {"name": "Thika", "lat": -1.0332, "lng": 37.0692, "county": "Kiambu"},
        {"name": "Machakos", "lat": -1.5177, "lng": 37.2634, "county": "Machakos"},
        {"name": "Nyeri", "lat": -0.4167, "lng": 36.9500, "county": "Nyeri"},
        {"name": "Meru", "lat": 0.0500, "lng": 37.6500, "county": "Meru"},
        {"name": "Kakamega", "lat": 0.2827, "lng": 34.7519, "county": "Kakamega"},
        {"name": "Kisii", "lat": -0.6817, "lng": 34.7680, "county": "Kisii"},
        {"name": "Kericho", "lat": -0.3689, "lng": 35.2831, "county": "Kericho"},
        {"name": "Malindi", "lat": -3.2192, "lng": 40.1169, "county": "Kilifi"},
        {"name": "Garissa", "lat": -0.4536, "lng": 39.6461, "county": "Garissa"},
        {"name": "Kitale", "lat": 1.0157, "lng": 35.0062, "county": "Trans-Nzoia"},
        {"name": "Naivasha", "lat": -0.7167, "lng": 36.4333, "county": "Nakuru"},
        {"name": "Nyahururu", "lat": 0.0333, "lng": 36.3667, "county": "Laikipia"},
        {"name": "Isiolo", "lat": 0.3546, "lng": 37.5822, "county": "Isiolo"},
        {"name": "Lamu", "lat": -2.2717, "lng": 40.9020, "county": "Lamu"},
        {"name": "Voi", "lat": -3.3833, "lng": 38.5667, "county": "Taita-Taveta"},
    ]
    
    map_data = []
    for city in kenya_cities:
        if city["name"] in ["Mombasa", "Malindi", "Lamu", "Voi"]:
            temp = round(random.uniform(26, 32), 1)
            humidity = random.randint(75, 90)
            rainfall = round(random.uniform(0, 15), 1)
        elif city["name"] in ["Eldoret", "Kericho", "Nyeri", "Nyahururu"]:
            temp = round(random.uniform(15, 22), 1)
            humidity = random.randint(65, 85)
            rainfall = round(random.uniform(5, 30), 1)
        else:
            temp = round(random.uniform(18, 26), 1)
            humidity = random.randint(55, 80)
            rainfall = round(random.uniform(0, 20), 1)
        
        risk_score = 0
        if rainfall > 20: risk_score += 3
        elif rainfall > 10: risk_score += 2
        elif rainfall > 5: risk_score += 1
        
        flood_prone = ["Mombasa", "Kisumu", "Garissa", "Malindi", "Lamu", "Nairobi"]
        if city["name"] in flood_prone: risk_score += 1
        
        if risk_score >= 4:
            risk_level = "high"
            confidence = round(random.uniform(88, 95), 1)
        elif risk_score >= 2:
            risk_level = "medium"
            confidence = round(random.uniform(80, 90), 1)
        else:
            risk_level = "low"
            confidence = round(random.uniform(85, 95), 1)
        
        if rainfall > 15:
            description = "Heavy Rain"
        elif rainfall > 5:
            description = "Light Rain"
        elif humidity > 75:
            description = "Cloudy"
        else:
            description = "Partly Cloudy"
        
        map_data.append({
            "name": city["name"],
            "county": city["county"],
            "lat": city["lat"],
            "lng": city["lng"],
            "risk_level": risk_level,
            "temperature": temp,
            "humidity": humidity,
            "rainfall": rainfall,
            "description": description,
            "confidence": confidence
        })
    
    return jsonify(map_data)


# ═══════════════════════════════════════════════════════════
# ANALYTICS ROUTES
# ═══════════════════════════════════════════════════════════

@main.route('/analytics')
@login_required
def analytics():
    if current_user.role == 'admin':
        return render_template('admin_analytics.html', user=current_user)
    else:
        return render_template('user_analytics.html', user=current_user)


@main.route('/api/analytics/admin')
@login_required
def api_admin_analytics():
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    from datetime import timedelta
    
    total_users = User.query.filter_by(role='commuter').count()
    total_chats = Chat.query.count()
    total_reports = FloodReport.query.count()
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0)
    chats_today = Chat.query.filter(Chat.timestamp >= today).count()
    
    high_risk = Chat.query.filter_by(risk_level='high').count()
    medium_risk = Chat.query.filter_by(risk_level='medium').count()
    low_risk = Chat.query.filter_by(risk_level='low').count()
    
    top_roads = db.session.query(
        Chat.road_queried,
        db.func.count(Chat.id).label('count')
    ).filter(Chat.road_queried != '', Chat.road_queried != None)\
     .group_by(Chat.road_queried)\
     .order_by(db.func.count(Chat.id).desc())\
     .limit(5).all()
    
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_chats = db.session.query(
        db.func.date(Chat.timestamp).label('date'),
        db.func.count(Chat.id).label('count')
    ).filter(Chat.timestamp >= seven_days_ago)\
     .group_by(db.func.date(Chat.timestamp)).all()
    
    users_by_location = db.session.query(
        User.location,
        db.func.count(User.id).label('count')
    ).filter_by(role='commuter').group_by(User.location).all()
    
    return jsonify({
        "totals": {
            "users": total_users,
            "chats": total_chats,
            "reports": total_reports,
            "chats_today": chats_today
        },
        "risk_distribution": {
            "high": high_risk,
            "medium": medium_risk,
            "low": low_risk
        },
        "top_roads": [{"road": r[0], "count": r[1]} for r in top_roads],
        "daily_chats": [{"date": str(d[0]), "count": d[1]} for d in daily_chats],
        "users_by_location": [{"location": l[0], "count": l[1]} for l in users_by_location]
    })


@main.route('/api/analytics/user')
@login_required
def api_user_analytics():
    from datetime import timedelta
    
    user_id = current_user.id
    
    total_chats = Chat.query.filter_by(user_id=user_id).count()
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0)
    chats_today = Chat.query.filter(
        Chat.user_id == user_id,
        Chat.timestamp >= today
    ).count()
    
    week_ago = datetime.utcnow() - timedelta(days=7)
    chats_this_week = Chat.query.filter(
        Chat.user_id == user_id,
        Chat.timestamp >= week_ago
    ).count()
    
    days_active = (datetime.utcnow() - current_user.created_at).days if current_user.created_at else 0
    
    high_risk = Chat.query.filter_by(user_id=user_id, risk_level='high').count()
    medium_risk = Chat.query.filter_by(user_id=user_id, risk_level='medium').count()
    low_risk = Chat.query.filter_by(user_id=user_id, risk_level='low').count()
    
    top_roads = db.session.query(
        Chat.road_queried,
        db.func.count(Chat.id).label('count')
    ).filter(
        Chat.user_id == user_id,
        Chat.road_queried != '',
        Chat.road_queried != None
    ).group_by(Chat.road_queried)\
     .order_by(db.func.count(Chat.id).desc())\
     .limit(5).all()
    
    daily_chats = db.session.query(
        db.func.date(Chat.timestamp).label('date'),
        db.func.count(Chat.id).label('count')
    ).filter(
        Chat.user_id == user_id,
        Chat.timestamp >= week_ago
    ).group_by(db.func.date(Chat.timestamp)).all()
    
    return jsonify({
        "totals": {
            "total_chats": total_chats,
            "chats_today": chats_today,
            "chats_this_week": chats_this_week,
            "days_active": days_active
        },
        "risk_distribution": {
            "high": high_risk,
            "medium": medium_risk,
            "low": low_risk
        },
        "top_roads": [{"road": r[0], "count": r[1]} for r in top_roads],
        "daily_chats": [{"date": str(d[0]), "count": d[1]} for d in daily_chats]
    })


# ═══════════════════════════════════════════════════════════
# ADMIN ROUTES
# ═══════════════════════════════════════════════════════════

@main.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('main.chat'))
    
    total_users = User.query.filter_by(role='commuter').count()
    total_chats = Chat.query.count()
    total_reports = FloodReport.query.count()
    
    recent_chats = Chat.query.order_by(Chat.timestamp.desc()).limit(10).all()
    
    stats = {
        'total_users': total_users,
        'total_chats': total_chats,
        'total_reports': total_reports,
    }
    
    return render_template('admin.html', 
                         user=current_user,
                         stats=stats,
                         recent_chats=recent_chats)


# ═══════════════════════════════════════════════════════════
# SMS ROUTES
# ═══════════════════════════════════════════════════════════

@main.route('/api/sms/send-alert', methods=['POST'])
@login_required
def api_send_sms_alert():
    """Send flood alert SMS to current user"""
    data = request.get_json()
    road_name = data.get('road_name', 'Unknown Road')
    risk_level = data.get('risk_level', 'medium')
    
    if not current_user.phone:
        return jsonify({
            "success": False,
            "message": "No phone number on file. Update your profile."
        }), 400
    
    result = sms_service.send_flood_alert(
        phone=current_user.phone,
        road_name=road_name,
        risk_level=risk_level,
        location=current_user.location
    )
    
    if result['success']:
        return jsonify({"success": True, "message": "SMS alert sent!"})
    else:
        return jsonify({"success": False, "message": result.get('error', 'Failed')})


@main.route('/api/sms/emergency-broadcast', methods=['POST'])
@login_required
def api_emergency_broadcast():
    """Admin sends emergency SMS to all users"""
    if current_user.role != 'admin':
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    message = data.get('message', '').strip()
    location_filter = data.get('location', None)
    
    if not message:
        return jsonify({"success": False, "message": "Message required"}), 400
    
    query = User.query.filter(
        User.role == 'commuter',
        User.phone != None,
        User.phone != ''
    )
    
    if location_filter:
        query = query.filter_by(location=location_filter)
    
    users = query.all()
    phones = [u.phone for u in users if u.phone]
    
    if not phones:
        return jsonify({"success": False, "message": "No users with phone numbers"}), 400
    
    result = sms_service.send_emergency_broadcast(phones, message)
    
    if result['success']:
        return jsonify({
            "success": True,
            "message": f"SMS sent to {len(phones)} users!",
            "count": len(phones)
        })
    else:
        return jsonify({"success": False, "message": result.get('error')})


@main.route('/admin/sms')
@login_required
def admin_sms_page():
    """Admin SMS broadcast page"""
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('main.chat'))
    
    users_with_phone = User.query.filter(
        User.role == 'commuter',
        User.phone != None,
        User.phone != ''
    ).count()
    
    total_users = User.query.filter_by(role='commuter').count()
    
    return render_template('admin_sms.html', 
                         user=current_user,
                         users_with_phone=users_with_phone,
                         total_users=total_users)