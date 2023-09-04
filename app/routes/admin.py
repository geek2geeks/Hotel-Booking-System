# Relative path: /c:/Users/ukped/OneDrive - RTC Education Ltd/Desktop/hotel booking system/Hotel-Booking-System/app/routes/admin.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import Room, User, Amenity  # Importing Amenity model
from functools import wraps
from flask_login import login_required, current_user
from app.extensions import db

admin = Blueprint('admin', __name__)

# Decorator to check if user has admin rights
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Access restricted to admins.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# Admin dashboard route with admin decorator applied
@admin.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/admin_dashboard.html')

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

        db.session.add(room)
        db.session.commit()
        flash('Room added successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/add_room.html')

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

