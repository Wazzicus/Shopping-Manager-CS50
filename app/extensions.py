"""
extensions.py

Initializes Flask extensions used across the app. These are imported and initialized
once here, and later linked to the Flask app in the application factory or main script.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect

# ORM: Handles models and database operations
db = SQLAlchemy()

# DB migrations: Handles schema versioning
migrate = Migrate()

# User session management
login_manager = LoginManager()

# Password hashing
bcrypt = Bcrypt()

# CSRF protection for WTForms
csrf = CSRFProtect()
