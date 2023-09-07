# File: Hotel-Booking-System/app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import User
from flask_login import login_user, logout_user, current_user, login_required
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
                    if next_page and "/admin/" not in next_page:
                        return redirect(next_page)
                    return redirect(url_for('customers.index'))
            else:
                flash('Invalid email or password', 'danger')
        except ValueError as ve:
            flash(str(ve), 'danger')
        except Exception as e:
            print("Error during login:", str(e))
            flash('An unexpected error occurred. Please try again.', 'danger')

    return render_template('customers/login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('customers.index'))

    # Check if any admin users exist
    no_admins = not User.query.filter_by(is_admin=True).first()

    if request.method == 'POST':
        try:
            username = request.form.get('username', default=None)
            email = request.form.get('email', default=None)
            password = request.form.get('password', default=None)
            confirm_password = request.form.get('confirm_password', default=None)
            
            # Check if all fields are provided
            if not username or not email or not password or not confirm_password:
                raise ValueError('All fields (Username, Email, Password, and Confirm Password) are required!')

            # Password match check
            if password != confirm_password:
                raise ValueError('Password and Confirm Password do not match.')

            # Email and username uniqueness checks
            if User.query.filter_by(email=email).first():
                raise ValueError('Email address already registered.')
            if User.query.filter_by(username=username).first():
                raise ValueError('Username already taken.')

            # Create the new User instance
            user = User(username=username, email=email)
            user.set_password(password)

            # If no admins and the checkbox is checked, make this user an admin
            if no_admins and request.form.get('register_as_admin'):
                user.is_admin = True

            # Add to db and commit
            db.session.add(user)
            db.session.commit()

            # Log them in and redirect
            login_user(user)
            flash('Registration successful. Welcome!', 'success')
            return redirect(url_for('customers.index'))
        except ValueError as e:
            flash(str(e), 'danger')
            return redirect(url_for('auth.register'))
        except Exception as e:
            db.session.rollback()  # Roll back any failed database transactions
            flash('Error registering the user. Please try again.', 'danger')

    # Pass the no_admins flag to the template to control the display of the admin registration option
    return render_template('customers/register.html', no_admins=no_admins)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('customers.index'))
