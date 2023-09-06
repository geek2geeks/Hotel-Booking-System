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
        return redirect(url_for('customers.index'))

    if request.method == 'POST':
        try:
            email = request.form.get('email', default=None)
            password = request.form.get('password', default=None)
            
            if not email or not password:
                raise ValueError('Email or Password is missing.')
            
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user)
                if user.is_admin:
                    return redirect(url_for('admin.admin_dashboard'))
                else:
                    next_page = request.args.get('next')
                    # Check if non-admin user is trying to access an admin-only route
                    if next_page and "/admin/" not in next_page:
                        return redirect(next_page)
                    return redirect(url_for('customers.index'))
            else:
                flash('Invalid email or password', 'danger')
        except ValueError as ve:
            flash(str(ve), 'danger')
        except Exception as e:
            # Log the error for developer reference
            print("Error during login:", str(e))
            flash('An unexpected error occurred. Please try again.', 'danger')

    return render_template('customers/login.html')




@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('customers.index'))

    if request.method == 'POST':
        try:
            email = request.form.get('email', default=None)
            password = request.form.get('password', default=None)
            
            if not email or not password:
                raise ValueError('Both email and password are required!')

            if User.query.filter_by(email=email).first():
                raise ValueError('Email address already registered')

            user = User(email=email)
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            login_user(user)
            flash('Registration successful. Welcome!', 'success')
            return redirect(url_for('customers.index'))
        except ValueError as e:
            flash(str(e), 'danger')
            return redirect(url_for('auth.register'))
        except Exception as e:
            db.session.rollback()
            flash('Error registering the user. Please try again.', 'danger')

    return render_template('customers/register.html')

# Route to log out the user
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('customers.index'))
