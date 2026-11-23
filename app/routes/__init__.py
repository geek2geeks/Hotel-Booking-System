# File location: Hotel-Booking-System/app/routes/__init__.py

from flask import Flask
import os

def create_app():
    # Setting the paths for templates and static directories
    template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    # Initialize Flask app with template and static paths
    app = Flask(__name__, template_folder=template_path)

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    # Optional local overrides: <repo>/instance/config.py (untracked, see .gitignore).
    try:
        app.config.from_object('instance.config.DevConfig')
    except (ImportError, AttributeError):
        pass

    # Environment-first configuration; the fallback keeps a fresh clone usable.
    app.config['SECRET_KEY'] = (
        os.environ.get('SECRET_KEY')
        or app.config.get('SECRET_KEY')
        or 'dev-only-insecure-key'
    )
    default_db_uri = 'sqlite:///' + os.path.join(base_dir, 'site.db').replace(os.sep, '/')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        os.environ.get('DATABASE_URL')
        or app.config.get('SQLALCHEMY_DATABASE_URI')
        or default_db_uri
    )
    
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
