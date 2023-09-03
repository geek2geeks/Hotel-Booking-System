from flask import render_template, redirect, url_for, flash, request
from app import app, db
from app.models import User, Room, Booking
from flask_login import login_user, logout_user, login_required, current_user
from app import login_manager 
from datetime import datetime
from sqlalchemy import or_, and_


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    rooms = Room.query.all()  
    return render_template('index.html', rooms=rooms)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if email or password fields are empty
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

@app.route('/search_rooms', methods=['POST'])
def search_rooms():
    search_term = request.form.get('search_term', '').strip()
    start_date_str = request.form.get('start_date', '').strip()
    end_date_str = request.form.get('end_date', '').strip()

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
        # Filter out rooms that are already booked within the date range
        subquery = Booking.query.filter(
            and_(
                Booking.start_date < end_date,
                Booking.end_date > start_date
            )
        ).with_entities(Booking.room_id).subquery()

        query = query.filter(~Room.id.in_(subquery))

    rooms = query.all()

    return render_template('index.html', rooms=rooms)``


@app.route('/dashboard')
@login_required
def dashboard():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()  # Assuming there's a Booking model
    return render_template('dashboard.html', bookings=bookings)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:   
        flash('Access restricted to admins.', 'danger')
        return redirect(url_for('index'))
    # Additional admin-specific logic can go here
    return render_template('admin/admin_dashboard.html')

@app.route('/admin/add-room', methods=['GET', 'POST'])
@login_required
def add_room():
    if not current_user.is_admin:
        flash('Only admins can add rooms.', 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        room = Room(name=request.form['name'], description=request.form['description'])  # Add more fields as necessary
        db.session.add(room)
        db.session.commit()
        flash('Room added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/add_room.html')


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
        room.description = request.form['description']  # Add more fields as necessary
        db.session.commit()
        flash('Room edited successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/edit_room.html', room=room)


@app.route('/admin/manage-users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Only admins can manage users.', 'danger')
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))