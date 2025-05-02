"""
Application initialization functions and logging configuration.
"""

# Standard library imports
import os
import logging
from logging.handlers import RotatingFileHandler

# Related third-party imports
from dotenv import load_dotenv
from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException

# Local application/library imports
from app.db import db


# Load environment variables from .env file
load_dotenv()

# Initialize Flask extensions
migrate = Migrate()
mail = Mail()


def configure_logging(app):
    """
    Configure logging for the Flask application.
    Args:
        app (Flask): The Flask application instance.
    """
    # Set up logging to a file
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        f"{log_dir}/app.log", maxBytes=1_000_000, backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    ))

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Clear existing handlers if running in debug/reload mode
    if app.logger.hasHandlers():
        app.logger.handlers.clear()

    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)

    # Log unhandled exceptions
    @app.errorhandler(Exception)
    def handle_exception(e):
        # Let Flask handle HTTP errors (e.g., 404, 403)
        if isinstance(e, HTTPException):
            return e
        
        app.logger.exception("Unhandled Exception: %s", e)
        return "An internal error occurred.", 500


def register_blueprints(app):
    """
    Register all blueprints for the Flask application.
    Args:
        app (Flask): The Flask application instance.
    """
    # Register blueprints for different modules
    from app.auth import bp as auth_bp
    from app.recipes import bp as recipes_bp
    from app.menus import bp as menus_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(recipes_bp)
    app.register_blueprint(menus_bp)


def create_app():
    """
    Create and configure the Flask application.
    Returns:
        Flask app: The configured Flask application instance.
    """
    # Create the Flask application
    app = Flask(__name__)

    # Load configuration from environment variables
    config_name = os.getenv("FLASK_CONFIG", "config.DevelopmentConfig")
    app.config.from_object(config_name)
    app.logger.info(f"Starting app in {config_name} mode.")

    # Initialize the database with the app
    db.init_app(app)

    # Register Blueprints
    register_blueprints(app)

    # Use Flask-Migrate for database changes
    migrate.init_app(app, db)

    # Initialize Flask-Mail
    mail.init_app(app)

    # Configure logging
    configure_logging(app)
    
    return app