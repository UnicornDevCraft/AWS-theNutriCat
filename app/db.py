""" Database connection module """
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_app(app):
    """Initialize the database"""
    db.init_app(app)
