# Imports
from flask import render_template, redirect, url_for, flash, request
from app import app, db, login_manager
from app.models import User, Room, Booking
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from sqlalchemy import or_, and_
from werkzeug.exceptions import BadRequestKeyError

# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route
@app.route('/')
def index():
    rooms = Room.query.all()
    return render_template('index.html', rooms=rooms)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if the user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # POST method for form submission
    if request.method == 'POST':
        try:
            # Fetch user from the database using the provided email
            user = User.query.filter_by(email=request.form['email']).first()

            # Check if user exists and the provided password is correct
            if user and user.check_password(request.form['password']):
                login_user(user)
                return redirect(request.args.get('next') or url_for('index'))
            else:
                flash('Invalid email or password', 'danger')
        except BadRequestKeyError:
            flash('Email field missing.', 'danger')
        except Exception as e:
            flash(str(e), 'danger')  # Flash any exception for debugging purposes.

    # Render the login form
    return render_template('login.html')


# Registration route
@app.route('/register', methods=['GET', 'POST'])
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

# Room search route
@app.route('/search_rooms', methods=['POST'])
def search_rooms():
    room_type = request.form.get('roomType')
    start_date_str = request.form.get('start_date', '').strip()
    end_date_str = request.form.get('end_date', '').strip()
    search_term = request.form.get('searchTerm', '').strip()

    try:
        start_date = datetime.strptime(start_date_str, '%m/%d/%Y') if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%m/%d/%Y') if end_date_str else None
    except ValueError:
        flash('Invalid date format. Please select valid dates.', 'danger')
        return redirect(url_for('index'))

    query = Room.query

    if search_term:
        query = query.filter(Room.name.ilike(f'%{search_term}%'))

    if start_date and end_date:
        subquery = Booking.query.filter(
            and_(
                Booking.start_date < end_date,
                Booking.end_date > start_date
            )
        ).with_entities(Booking.room_id).subquery()

        query = query.filter(~Room.id.in_(subquery))

    if room_type:
        query = query.filter(Room.type == room_type)

    rooms = query.all()

    return render_template('index.html', rooms=rooms)

# User's dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', bookings=bookings)

# Admin's dashboard route
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access restricted to admins.', 'danger')
        return redirect(url_for('index'))
    
    return render_template('admin/admin_dashboard.html')

# Admin route to add a new room
@app.route('/admin/add-room', methods=['GET', 'POST'])
@login_required
def add_room():
    if not current_user.is_admin:
        flash('Only admins can add rooms.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        room = Room(name=request.form['name'], description=request.form['description'])
        db.session.add(room)
        db.session.commit()
        flash('Room added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/add_room.html')

# Admin route to edit an existing room
@app.route('/admin/edit-room/<int:room_id>', methods=['GET', 'POST'])
@login_required
def edit_room(room_id):
    if not current_user.is_admin:
        flash('Only admins can edit rooms.', 'danger')
        return redirect(url_for('index'))

    room = Room.query.get(room_id)
    if not room:
        flash('Room not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        room.name = request.form['name']
        room.description = request.form['description']
        db.session.commit()
        flash('Room edited successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/edit_room.html', room=room)

# Admin route to manage users
@app.route('/admin/manage-users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Only admins can manage users.', 'danger')
        return redirect(url_for('index'))

    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@app.route('/init_admin')
def init_admin():
    if not User.query.filter_by(email='admin@admin.com').first():
        user = User(username='admin', email='admin@admin.com', is_admin=True)
        user.set_password('As!101010')
        db.session.add(user)
        db.session.commit()
        flash('Admin initialized!', 'success')
    else:
        flash('Admin already exists!', 'danger')
    return redirect(url_for('index'))

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
