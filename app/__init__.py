from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object('instance.config.DevConfig')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import views, models
