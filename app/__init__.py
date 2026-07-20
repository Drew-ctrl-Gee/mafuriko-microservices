"""MafurikoAI Flask Application Factory"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_mail import Mail
from config import Config
import os

# Initialize extensions
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
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    # Create database
    with app.app_context():
        db.create_all()
        create_default_admin(app)
    
    return app


def create_default_admin(app):
    """Create default admin"""
    from app.models import User
    import bcrypt
    
    admin = User.query.filter_by(username=app.config['ADMIN_USERNAME']).first()
    
    if not admin:
        pass_hash = bcrypt.hashpw(
            app.config['ADMIN_PASSWORD'].encode('utf-8'),
            bcrypt.gensalt()
        )
        
        admin_user = User(
            username=app.config['ADMIN_USERNAME'],
            email=app.config['ADMIN_EMAIL'],
            password_hash=pass_hash.decode('utf-8'),
            role='admin',
            location='Nairobi',
            language='en'
        )
        db.session.add(admin_user)
        db.session.commit()
        print(f"✅ Default admin created: {app.config['ADMIN_USERNAME']}")