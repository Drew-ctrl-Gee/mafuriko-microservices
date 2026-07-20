"""
MafurikoAI - Auth Microservice
Handles authentication and JWT tokens
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import jwt
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

# Database - Same SQLite as your existing app!
basedir = os.path.abspath(os.path.dirname(__file__))
# Use local database inside container
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'sqlite:////app/data/mafuriko.db'
)

# Ensure data directory exists
os.makedirs('/app/data', exist_ok=True)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'auth-secret-key-2025')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='commuter')
    location = db.Column(db.String(100), default='Nairobi')
    language = db.Column(db.String(5), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)


with app.app_context():
    db.create_all()


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "service": "auth-service",
        "status": "healthy",
        "port": os.getenv('PORT', 5001),
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"success": False, "error": "Username already exists"}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"success": False, "error": "Email already exists"}), 400
    
    pass_hash = bcrypt.hashpw(
        data['password'].encode('utf-8'),
        bcrypt.gensalt()
    )
    
    user = User(
        username=data['username'],
        email=data['email'],
        phone=data.get('phone', ''),
        password_hash=pass_hash.decode('utf-8'),
        location=data.get('location', 'Nairobi'),
        role='commuter'
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "Account created successfully",
        "user_id": user.id
    })


@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    user = User.query.filter(
        (User.username == data['username']) | 
        (User.email == data['username'])
    ).first()
    
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 401
    
    if not bcrypt.checkpw(
        data['password'].encode('utf-8'),
        user.password_hash.encode('utf-8')
    ):
        return jsonify({"success": False, "error": "Invalid password"}), 401
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Generate JWT
    token = jwt.encode({
        'user_id': user.id,
        'username': user.username,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "location": user.location,
            "language": user.language
        }
    })


@app.route('/api/auth/verify', methods=['POST'])
def verify_token():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        return jsonify({"valid": False, "error": "No token provided"}), 401
    
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({
            "valid": True,
            "user_id": payload['user_id'],
            "username": payload['username'],
            "role": payload['role']
        })
    except jwt.ExpiredSignatureError:
        return jsonify({"valid": False, "error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"valid": False, "error": "Invalid token"}), 401


@app.route('/api/auth/users', methods=['GET'])
def list_users():
    """Get all users (admin endpoint)"""
    users = User.query.all()
    return jsonify({
        "total": len(users),
        "users": [{
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "location": u.location,
            "created_at": u.created_at.isoformat() if u.created_at else None
        } for u in users]
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    print(f"🔐 Auth Service starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)