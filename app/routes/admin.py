# Relative path: /c:/Users/ukped/OneDrive - RTC Education Ltd/Desktop/hotel booking system/Hotel-Booking-System/app/routes/admin.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from app.models import Room, User, Amenity, Booking, Photo
from functools import wraps
from flask_login import login_required, current_user
from app.extensions import db
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
import os

admin = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Decorator to check if user has admin rights
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Access restricted to admins.', 'danger')
            return redirect(url_for('customers.index'))
        return f(*args, **kwargs)
    return decorated_function

# Error Handler for Database Errors
@admin.errorhandler(IntegrityError)
def handle_db_error(e):
    db.session.rollback()
    flash('A database error occurred. Please try again.', 'danger')
    return redirect(url_for('admin.admin_dashboard'))

# General Error Handling
@admin.errorhandler(500)  # Internal Server Error
def handle_generic_error(e):
    flash('An unexpected error occurred. Please try again later.', 'danger')
    return redirect(url_for('admin.admin_dashboard'))

# Custom Error Messages
class CustomError(Exception):
    pass

@admin.errorhandler(CustomError)
def handle_custom_error(e):
    flash(str(e), 'danger')
    return redirect(url_for('admin.admin_dashboard'))

# Handling Not Found (404) Errors
@admin.errorhandler(404)
def handle_not_found(e):
    flash('The resource you are looking for was not found.', 'warning')
    return redirect(url_for('admin.admin_dashboard'))

# Admin dashboard route with admin decorator applied
@admin.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/admin_dashboard.html')

@admin.route('/booking/<int:booking_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))
    
    room_id = booking.room_id
    db.session.delete(booking)
    db.session.commit()
    flash('Booking deleted successfully!', 'success')
    return redirect(url_for('admin.view_room_bookings', room_id=room_id))


# Admin route to add a new room with admin decorator applied
@admin.route('/add-room', methods=['GET', 'POST'])
@login_required
@admin_required
def add_room():
    if request.method == 'POST':
        room = Room(room_number=request.form['room_number'], type=request.form['room_type'], price=request.form['room_price'])
        
        # Fetch selected amenities and associate with the room
        selected_amenities = request.form.getlist('amenities')
        room.amenities = Amenity.query.filter(Amenity.name.in_(selected_amenities)).all()

        # Handle the photos upload
        if 'photos' in request.files:
            for photo in request.files.getlist('photos'):
                if photo and allowed_file(photo.filename):
                    filename = secure_filename(photo.filename)
                    # Make sure to create the room_photos directory in your static folder
                    photo_path = os.path.join(current_app.static_folder, 'room_photos', filename)
                    photo.save(photo_path)
                    new_photo = Photo(path=photo_path)
                    room.photos.append(new_photo)

        db.session.add(room)
        db.session.commit()
        flash('Room added successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/add_room.html')


@admin.route('/view-room-bookings/<int:room_id>', methods=['GET'])
@login_required
@admin_required
def view_room_bookings(room_id):
    room = Room.query.get(room_id)
    if not room:
        flash('Room not found.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))
    
    bookings = Booking.query.filter_by(room_id=room_id).all()  # Fetch bookings for this room
    
    return render_template('admin/view_room_bookings.html', room=room, bookings=bookings)

@admin.route('/list-rooms')
@admin_required
def list_rooms_for_admin():
    rooms = Room.query.all()
    return render_template('admin/all_rooms.html', rooms=rooms)

@admin.route('/delete-room/<int:room_id>', methods=['POST'])
@login_required
@admin_required
def delete_room(room_id):
    room = Room.query.get(room_id)
    if not room:
        flash('Room not found.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))
    
    db.session.delete(room)
    db.session.commit()
    flash('Room deleted!', 'success')
    return redirect(url_for('admin.admin_dashboard'))



@admin.route('/edit-room/<int:room_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_room(room_id):
    room = Room.query.get(room_id)
    if not room:
        flash('Room not found.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    if request.method == 'POST':
        room.room_number = request.form['room_number']
        room.type = request.form['room_type']
        room.price = float(request.form['room_price'])  # Ensure conversion to float for price
        
        # Update the amenities associated with the room
        selected_amenities = request.form.getlist('amenities')
        room.amenities = Amenity.query.filter(Amenity.name.in_(selected_amenities)).all()

        db.session.commit()
        flash('Room edited successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/edit_room.html', room=room)

@admin.route('/manage-users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@admin.route('/room/<int:room_id>', methods=['GET'])
@login_required
@admin_required
def view_room(room_id):
    room = Room.query.get(room_id)
    if not room:
        flash('Room not found.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))
    
    return render_template('admin/view_room.html', room=room)


@admin.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user_detail(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    if request.method == 'POST':
        user.email = request.form['email']
        user.is_admin = 'admin' in request.form  # Check a checkbox named 'admin' in the form
        db.session.commit()
        flash('User details updated!', 'success')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    return render_template('admin/user_detail.html', user=user)

@admin.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted!', 'success')
    return redirect(url_for('admin.manage_users'))

