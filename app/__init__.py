from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'As!101010'
app.config.from_object('instance.config.DevConfig')

# Initialize Flask extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)


# Import views and models after extensions are initialized
from app import views, models
