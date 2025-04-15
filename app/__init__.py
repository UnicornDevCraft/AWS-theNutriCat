from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate
from config import Config
from app.db import db
import os

migrate = Migrate()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)  # Initialize the database with the app
    migrate.init_app(app, db)  # Use Flask-Migrate for database changes

    # Register Blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.recipes import bp as recipes_bp
    app.register_blueprint(recipes_bp)

    # Add Flask-Mail configuration
    app.config['MAIL_SERVER'] = 'localhost'
    app.config['MAIL_PORT'] = 8025
    app.config['MAIL_DEFAULT_SENDER'] = 'noreply@nutricat.local'
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = ''
    app.config['MAIL_PASSWORD'] = ''

    mail.init_app(app)

    # Add Flask-Recaptcha configuration
    app.config['RECAPTCHA_SITE_KEY'] = os.getenv('RECAPTCHA_SITE_KEY')
    app.config['RECAPTCHA_SECRET_KEY'] = os.getenv('RECAPTCHA_SECRET_KEY')
    
    return app