# File: Hotel-Booking-System/app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import User
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import BadRequestKeyError
from app.extensions import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            email = request.form.get('email', default=None)
            password = request.form.get('password', default=None)
            
            if not email:
                raise BadRequestKeyError('Email field missing.')

            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user)

                # Redirect user based on role
                if user.is_admin:  # Assuming 'is_admin' is a boolean field in your User model
                    return redirect(url_for('admin.admin_dashboard'))  # Assuming 'admin_dashboard' is your admin dashboard route
                else:
                    return redirect(request.args.get('next') or url_for('main.index'))

            else:
                flash('Invalid email or password', 'danger')
        except BadRequestKeyError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(str(e), 'danger')

    return render_template('login.html')


# Route to register new users
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Both email and password are required!', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email address already registered', 'danger')
            return redirect(url_for('register'))

        user = User(email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        login_user(user)

        flash('Registration successful. Welcome!', 'success')
        return redirect(url_for('index'))

    return render_template('register.html')

# Route to log out the user
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))