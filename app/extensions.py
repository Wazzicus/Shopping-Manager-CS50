# extensions.py
# This file contains the initialization of Flask extensions used in the application.
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager =LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()
