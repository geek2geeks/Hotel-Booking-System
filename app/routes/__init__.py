# app/__init__.py

from flask import Flask
import os

def create_app():
    # Setting the paths for templates and static directories
    template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
    
    # Initialize Flask app
    app = Flask(__name__, template_folder=template_path, static_folder=static_path)
    # ... Rest of the code remains unchanged


    # Application secret key for sessions and cookies
    app.config['SECRET_KEY'] = 'As!101010'

    # Load configuration from instance folder
    app.config.from_object('instance.config.DevConfig')  
    
    # Bind app with Flask extensions
    from app.extensions import db, migrate, login_manager, bcrypt
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Import blueprints
    from app.routes.admin import admin
    from app.routes.auth import auth
    from app.routes.main import main

    # Register blueprints
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(main)

    # Import models and User Loader function for Flask-Login
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
