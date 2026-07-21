"""MafurikoAI Flask Application Factory"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_mail import Mail
from config import Config
import os

# Initialize extensions (WITHOUT app)
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

login_manager.login_view = 'main.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # ═══════════════════════════════════════════════════════
    # EMAIL CONFIGURATION
    # ═══════════════════════════════════════════════════════
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'false').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    
    # ═══════════════════════════════════════════════════════
    # DATABASE CONFIGURATION (Persistent!)
    # ═══════════════════════════════════════════════════════
    database_url = os.getenv('DATABASE_URL', 'sqlite:///mafuriko.db')
    # Fix for PostgreSQL URL prefix
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # ═══════════════════════════════════════════════════════
    # INITIALIZE EXTENSIONS WITH APP
    # ═══════════════════════════════════════════════════════
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    CORS(app)
    
    # ═══════════════════════════════════════════════════════
    # REGISTER BLUEPRINTS
    # ═══════════════════════════════════════════════════════
    from app.routes import main
    app.register_blueprint(main)
    
    # ═══════════════════════════════════════════════════════
    # CREATE DATABASE TABLES
    # ═══════════════════════════════════════════════════════
    with app.app_context():
        db.create_all()
        create_default_admin(app)
    
    return app


def create_default_admin(app):
    """Create default admin user if not exists"""
    from app.models import User
    import bcrypt
    
    admin = User.query.filter_by(username=app.config.get('ADMIN_USERNAME', 'admin')).first()
    
    if not admin:
        admin_password = app.config.get('ADMIN_PASSWORD', 'admin123')
        pass_hash = bcrypt.hashpw(
            admin_password.encode('utf-8'),
            bcrypt.gensalt()
        )
        
        admin_user = User(
            username=app.config.get('ADMIN_USERNAME', 'admin'),
            email=app.config.get('ADMIN_EMAIL', 'admin@mafuriko.ke'),
            password_hash=pass_hash.decode('utf-8'),
            role='admin',
            location='Nairobi',
            language='en'
        )
        db.session.add(admin_user)
        db.session.commit()
        print(f"✅ Default admin created: {app.config.get('ADMIN_USERNAME', 'admin')}")