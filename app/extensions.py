# extensions.py
# app/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# Initialize the extension for database operations
db = SQLAlchemy()

# Initialize the extension for database migrations
migrate = Migrate()

# Initialize the extension for user authentication
login_manager = LoginManager()

# Specify the view to redirect to when a user needs to log in
login_manager.login_view = 'login'

# Initialize the extension for password hashing
bcrypt = Bcrypt()
