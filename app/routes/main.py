# File: Hotel-Booking-System/app/routes/main.py

import os
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import Room, Booking
from datetime import datetime
from sqlalchemy import or_, and_
from flask import current_app as app
from app.extensions import db
from flask_login import login_required, current_user

template_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
print("Template Path: ", template_path)

main = Blueprint('main', __name__)

# Home route that displays all rooms
@main.route('/')
def index():
    rooms = Room.query.all()
    print("Template Path: ", app.template_folder)
    return render_template('index.html', rooms=rooms)

@main.route('/list-rooms')
@login_required
def list_rooms():
    rooms = Room.query.all()
    return render_template('list_rooms.html', rooms=rooms)

@main.route('/book-room/<int:room_id>', methods=['GET', 'POST'])
@login_required
def book_room(room_id):
    room = Room.query.get_or_404(room_id)
    
    # If request is a POST request, handle the booking form submission
    if request.method == 'POST':
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please select valid dates.', 'danger')
            return render_template('book_room.html', room=room)

        # Check if the room is available during the specified dates
        overlapping_bookings = Booking.query.filter(
            Booking.room_id == room_id,
            Booking.start_date < end_date,
            Booking.end_date > start_date
        ).count()

        # If overlapping bookings exist, show an error message
        if overlapping_bookings > 0:
            flash('Room is already booked during the specified dates.', 'danger')
            return render_template('book_room.html', room=room)

        # If room is available, create a new booking
        booking = Booking(user_id=current_user.id, room_id=room_id, start_date=start_date, end_date=end_date)
        db.session.add(booking)
        db.session.commit()
        flash('Room booked successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    # If request is a GET request, show the booking form
    return render_template('book_room.html', room=room)

# Search functionality for rooms
@main.route('/search_rooms', methods=['POST'])
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

# Route for the user's dashboard
@main.route('/dashboard')
@login_required
def dashboard():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('user_dashboard.html', bookings=bookings)
