# File location: Hotel-Booking-System/app/routes/__init__.py

from flask import Flask
import os

def create_app():
    # Setting the paths for templates and static directories
    template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    # Initialize Flask app with template and static paths
    app = Flask(__name__, template_folder=template_path)

    # Application secret key for sessions and cookies
    app.config['SECRET_KEY'] = 'As!101010'

    # Load configuration from instance folder
    # File location: Hotel-Booking-System/instance/config.py
    app.config.from_object('instance.config.DevConfig')  
    
    # Bind app with Flask extensions
    # File location: Hotel-Booking-System/app/extensions.py
    from app.extensions import db, migrate, login_manager, bcrypt
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    login_manager.login_view = 'auth.login'

    # Import blueprints
    # File locations: 
    # Hotel-Booking-System/app/routes/admin.py
    # Hotel-Booking-System/app/routes/auth.py
    # Hotel-Booking-System/app/routes/customers.py
    from .admin import admin
    from .auth import auth
    from .customers import customers
    
    # Register blueprints
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(customers, url_prefix='/')

    # Import models and User Loader function for Flask-Login
    # File location: Hotel-Booking-System/app/models.py
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
