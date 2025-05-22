"""
__init__.py

Flask application factory for the Shopping Manager app.

Responsibilities:
- Initializes the Flask app with configurations
- Registers blueprints for modular route organization
- Sets up Flask extensions (SQLAlchemy, LoginManager, CSRF, etc.)
- Ensures necessary upload folders exist
"""

from flask import Flask
import os

# Route blueprints
from .auth.routes import auth_bp
from .routes import main
from .household.routes import household_bp
from .shopping_lists.routes import shoppinglist_bp
from .settings.routes import settings_bp
from .files.routes import files_bp

# Configuration
from .config import Config

# Extensions
from app.extensions import db, bcrypt, login_manager, migrate, csrf

# Configure Flask-Login defaults
login_manager.login_view = 'auth.auth'  # Redirect to this endpoint if not logged in
login_manager.login_message = "Please login to access this page"
login_manager.login_message_category = "info"


def create_app():
    """
    Application factory function.

    Creates and configures the Flask application instance with:
    - Config object from config.py
    - Database and other extensions
    - Route blueprints
    - Upload directories
    - User loader for login sessions

    Returns:
        Flask app instance
    """
    app = Flask(
        __name__,
        template_folder=os.path.abspath("templates"),
        static_folder=os.path.abspath("static")
    )

    # Load configuration (default: from Config class)
    app.config.from_object(Config)

    # Setup upload folder paths
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/images/uploads')
    app.config['AVATAR_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'avatars')

    # Create upload directories if they don't already exist
    os.makedirs(app.config['AVATAR_FOLDER'], exist_ok=True)

    # Initialize extensions with the app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # Register route blueprints (modular structure)
    app.register_blueprint(main)
    app.register_blueprint(auth_bp)
    app.register_blueprint(household_bp, url_prefix='/household')
    app.register_blueprint(shoppinglist_bp, url_prefix='/shopping')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(files_bp, url_prefix='/files')

    # Import models to ensure they are registered before migrations
    with app.app_context():
        from .models import User  # Only importing what's needed here

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        """
        Callback to reload the user object from the user ID stored in the session.
        """
        return User.query.get(int(user_id))

    return app  # Return the fully configured Flask app
