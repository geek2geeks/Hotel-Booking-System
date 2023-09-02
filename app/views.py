from flask import render_template, redirect, url_for, flash, request
from app import app, db
from app.models import User, Room  # Assuming you have User and Room models defined in models.py
from flask_login import login_user, logout_user, login_required, current_user
# Add other necessary imports

@app.route('/')
def index():
    rooms = Room.query.all()  # Fetch all rooms. Adjust as needed.
    return render_template('index.html', rooms=rooms)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If the user is already logged in, redirect to home page
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # Handle POST request from login form here (e.g., verify password, log user in)
    # For now, just render the template
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Similar to login, handle registration logic here
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Assuming only authenticated users can access the dashboard
    return render_template('dashboard.html')

@app.route('/admin/add-room', methods=['GET', 'POST'])
@login_required
def add_room():
    # Ensure that the user is an admin before allowing them to add a room
    if not current_user.is_admin:
        flash('Only admins can add rooms.', 'danger')
        return redirect(url_for('index'))
    # Handle room addition logic here
    return render_template('add_room.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
