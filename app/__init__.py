from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

login_manager = LoginManager(app)
login_manager.login_view = 'login'

app = Flask(__name__)
app.config.from_object('instance.config.DevConfig')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import views, models
