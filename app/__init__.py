from flask import Flask
from flask_migrate import Migrate
from config import Config
from app.db import db

migrate = Migrate()

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
    
    return app