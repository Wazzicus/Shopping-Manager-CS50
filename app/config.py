"""
config.py

Configuration settings for the Flask application.

Uses environment variables when available, with defaults provided for development.
"""

import os

class Config:
    """
    Base configuration class.
    """
    # Flask secret key (used for sessions, CSRF protection, etc.)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'jDf#8PzL3rQ!2vXs@5TkW9^mNzH7aEY%UbV0oCMp&RgIqA1dFbJxG$ZKi^lueS')

    # Database connection URI
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///shopping_manager.db')

    # Disable modification tracking for SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Folder where avatar images are stored
    UPLOAD_FOLDER = 'static/images/avatars'

    # Allowed file extensions for image uploads
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
