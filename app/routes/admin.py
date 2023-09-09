# app/routes/admin.py

# Importing required modules and classes.
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from app.models import Room, User, Amenity, Booking, Photo
from functools import wraps
from flask_login import login_required, current_user
from app.extensions import db
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from flask import jsonify
import os

# Blueprint for the admin related routes.
admin = Blueprint('admin', __name__)

# Allowed file extensions for room photos.
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Helper function to check if uploaded file has allowed extensions.
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Decorator to restrict access only to admin users.
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Access restricted to admins.', 'danger')
            return redirect(url_for('costumers.index'))
        return f(*args, **kwargs)
    return decorated_function

# Error handlers for various exceptions that may arise.
@admin.errorhandler(IntegrityError)
def handle_db_error(e):
    db.session.rollback()
    flash('A database error occurred. Please try again.', 'danger')
    return redirect(url_for('admin.admin_dashboard'))

@admin.errorhandler(500)
def handle_generic_error(e):
    flash('An unexpected error occurred. Please try again later.', 'danger')
    return redirect(url_for('admin.admin_dashboard'))

@admin.errorhandler(404)
def handle_not_found(e):
    flash('The resource you are looking for was not found.', 'warning')
    return redirect(url_for('admin.admin_dashboard'))

# Route to bulk delete users.
@admin.route('/bulk-delete-users', methods=['POST'])
@login_required
@admin_required
def bulk_delete_users():
    user_ids = request.form.getlist('user_ids')  
    if not user_ids:
        flash('No users selected for deletion.', 'warning')
        return redirect(url_for('admin.manage_users'))
    User.query.filter(User.id.in_(user_ids)).delete(synchronize_session=False)
    db.session.commit()
    flash(f'{len(user_ids)} users deleted successfully!', 'success')
    return redirect(url_for('admin.manage_users'))

# Admin dashboard main route.
@admin.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/admin_dashboard.html')

# Route to list all rooms.
@admin.route('/list-rooms')
@admin_required
def list_rooms_for_admin():
    rooms = Room.query.all()
    return render_template('admin/manage_rooms.html', rooms=rooms)

# Route to manage all users.
@admin.route('/manage-users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

# Route to view a specific room.
@admin.route('/view-room/<int:room_id>', methods=['GET'])
@login_required
@admin_required
def view_room(room_id):
    room = Room.query.get(room_id)
    if not room:
        flash('Room not found.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('admin/manage_rooms.html', room=room)

# Route to view and edit details of a specific user.
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
        user.is_admin = 'admin' in request.form
        db.session.commit()
        flash('User details updated!', 'success')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    return render_template('admin/manage_users.html', user=user)

# Route to delete a specific user.
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

# Route for adding or editing a room.
@admin.route('/room-form/<int:room_id>', methods=['GET', 'POST'])
@admin.route('/room-form', defaults={'room_id': None}, methods=['GET', 'POST'])
@login_required
@admin_required
def room_form(room_id):
    room = Room.query.get(room_id) if room_id else None
    
    # Fetch all available amenities
    all_amenities = Amenity.query.all()

    if request.method == 'POST':
        if not room:
            room = Room()
            db.session.add(room)

        room.room_number = request.form['room_number']
        room.type = request.form['room_type']
        room.description = request.form['description']
        room.price = float(request.form['room_price'])
        
        # Updating the amenities based on their IDs
        selected_amenities_ids = [int(id) for id in request.form.getlist('amenities')]
        room.amenities = Amenity.query.filter(Amenity.id.in_(selected_amenities_ids)).all()

        if 'photos' in request.files:
            for photo in request.files.getlist('photos'):
                if photo and allowed_file(photo.filename):
                    filename = secure_filename(photo.filename)
                    photo_path_full = os.path.join(current_app.static_folder, 'room_photos', filename)
                    # Save the photo to the static folder
                    photo.save(photo_path_full)
                    # Only save the relative path to the database
                    relative_photo_path = os.path.join('room_photos', filename)
                    new_photo = Photo(path=relative_photo_path)
                    room.photos.append(new_photo)

        db.session.commit()
        flash(f"Room {'edited' if room_id else 'added'} successfully!", 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/room_form.html', room=room, amenities=all_amenities)



