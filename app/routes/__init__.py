from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# Initialize Flask app
app = Flask(__name__)
# Application secret key for sessions and cookies
app.config['SECRET_KEY'] = 'As!101010'
# Load configuration from instance folder
app.config.from_object('instance.config.DevConfig')  

# Initialize Flask extensions
db = SQLAlchemy(app)   # Database operations
migrate = Migrate(app, db)  # Database migrations
login_manager = LoginManager(app)  # User authentication
login_manager.login_view = 'login'  # View for logging in
bcrypt = Bcrypt(app)  # Password hashing

# Import views and models to avoid circular imports
from app import views, models

# User Loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
