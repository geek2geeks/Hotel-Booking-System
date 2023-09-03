# File: app/routes/admin.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.models import Room, User
from functools import wraps
from flask_login import login_required, current_user
from flask import current_app as app
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
        db.session.add(room)
        db.session.commit()
        flash('Room added successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/add_room.html')

# Admin route to edit an existing room with admin decorator applied
@admin.route('/edit-room/<int:room_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_room(room_id):
    room = Room.query.get(room_id)
    if not room:
        flash('Room not found.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

    if request.method == 'POST':
        room.name = request.form['name']
        room.description = request.form['description']
        db.session.commit()
        flash('Room edited successfully!', 'success')
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/edit_room.html', room=room)

# Admin route to manage users with admin decorator applied
@admin.route('/manage-users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)
