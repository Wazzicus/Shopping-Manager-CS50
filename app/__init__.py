from flask import Flask
import os
from .auth.routes import auth_bp
from .config import Config
from .routes import main
from .household.routes import household_bp
from .shopping_lists.routes import shoppinglist_bp
from .settings.routes import settings_bp
from app.extensions import db, bcrypt,login_manager,migrate,csrf

login_manager.login_view = 'auth.auth'
login_manager.login_message = "Please login to access this page"
login_manager.login_message_category = "info"    


def create_app():
    app = Flask(__name__, template_folder=os.path.abspath("templates"), static_folder=os.path.abspath("static"))

    app.config.from_object(Config)

    # Initialisation of extensions.
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)


    # Registers routes
    app.register_blueprint(main)
    app.register_blueprint(auth_bp)
    app.register_blueprint(household_bp, url_prefix='/household')
    app.register_blueprint(shoppinglist_bp, url_prefix='/shopping')
    app.register_blueprint(settings_bp, url_prefix='/settings')

    # Import models from models.py
    with app.app_context():
        from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Return app instance.    
    return app