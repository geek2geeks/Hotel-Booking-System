# File: Hotel-Booking-System/app/routes/customers.py
# Standard library imports
import os
from datetime import datetime
from functools import wraps

# Third-party library imports
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app as app
from sqlalchemy import or_, and_
from flask_login import login_required, current_user

# Local application/library specific imports
from app.models import Room, Booking
from app.extensions import db

customers = Blueprint('customers', __name__)

DATE_FORMAT = '%Y-%m-%d'

def role_required(is_admin: bool):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.is_admin != is_admin:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('customers.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

customer_required = role_required(is_admin=False)
admin_required = role_required(is_admin=True)

@customers.route('/')
def index():
    return render_template('customers/index.html')

@customers.route('/list-rooms')
@login_required
@customer_required
def list_rooms():
    rooms = Room.query.all()
    return render_template('customers/list.rooms.html', rooms=rooms)

@customers.route('/book-room/<int:room_id>', methods=['GET', 'POST'])
@login_required
@customer_required
def book_room(room_id):
    room = Room.query.get_or_404(room_id)
    
    if request.method == 'POST':
        try:
            start_date_str = request.form.get('start_date', '').strip()
            end_date_str = request.form.get('end_date', '').strip()
            start_date = datetime.strptime(start_date_str, DATE_FORMAT)
            end_date = datetime.strptime(end_date_str, DATE_FORMAT)

            overlapping_bookings = Booking.query.filter(
                Booking.room_id == room_id,
                Booking.start_date < end_date,
                Booking.end_date > start_date
            ).count()

            if overlapping_bookings > 0:
                raise ValueError('Room is already booked during the specified dates.')

            booking = Booking(user_id=current_user.id, room_id=room_id, start_date=start_date, end_date=end_date)
            booking.calculate_total_price()
            db.session.add(booking)
            db.session.commit()
            flash('Room booked successfully!', 'success')
            return redirect(url_for('customers.dashboard'))
        except ValueError as e:
            flash(str(e), 'danger')
            print(f"ValueError: {str(e)}")
        except Exception as e:
            db.session.rollback()
            flash('Error booking the room. Please try again.', 'danger')
            print(f"Error: {str(e)}")

    return render_template('customers/book_room.html', room=room)

@customers.route('/search_rooms', methods=['POST'])
def search_rooms():
    room_type = request.form.get('roomType')
    start_date_str = request.form.get('start_date', '').strip()
    end_date_str = request.form.get('end_date', '').strip()
    search_term = request.form.get('searchTerm', '').strip()

    try:
        start_date = datetime.strptime(start_date_str, DATE_FORMAT) if start_date_str else None
        end_date = datetime.strptime(end_date_str, DATE_FORMAT) if end_date_str else None
    except ValueError:
        flash('Invalid date format. Please select valid dates.', 'danger')
        return redirect(url_for('customers.index'))

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

    return render_template('customers/index.html', rooms=rooms)

@customers.route('/dashboard')
@login_required
@customer_required
def dashboard():
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    return render_template('customers/user_dashboard.html', bookings=bookings)
