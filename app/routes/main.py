from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import Room, Booking
from datetime import datetime
from sqlalchemy import or_, and_
from app import app, db
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

# Home route that displays all rooms
@main.route('/')
def index():
    rooms = Room.query.all()
    return render_template('index.html', rooms=rooms)

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
    return render_template('dashboard.html', bookings=bookings)
