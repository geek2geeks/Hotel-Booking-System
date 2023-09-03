# models.py
from datetime import datetime
from app.routes import db, bcrypt
from enum import Enum
from flask_login import UserMixin

# Enum to represent room status
class RoomStatus(Enum):
    OCCUPIED = 'occupied'
    AVAILABLE = 'available'

# Association table to establish many-to-many relationship between Room and Amenity
room_amenities = db.Table('room_amenities',
    db.Column('room_id', db.Integer, db.ForeignKey('room.id')),  # Foreign key for room
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenity.id'))  # Foreign key for amenity
)

# Model to represent a User
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='guest', lazy=True)  # Establish relationship with Booking model

    @property
    def is_active(self):
        # This can be used to check if a user is active, further logic can be added as needed
        return True

    def set_password(self, password):
        # Set password hash for the user
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        # Check the provided password against stored password hash
        return bcrypt.check_password_hash(self.password_hash, password)

# Model to represent a Room
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    amenities = db.relationship('Amenity', secondary=room_amenities, backref='rooms')  # Many-to-many relationship with Amenity
    bookings = db.relationship('Booking', backref='room', lazy=True)  # One-to-many relationship with Booking

    @property
    def status(self):
        # Determine if room is occupied based on bookings
        for booking in self.bookings:
            if booking.start_date <= datetime.utcnow() <= booking.end_date:
                return 'occupied'
        return 'available'

# Model to represent an Amenity
class Amenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

# Model to represent a Booking
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key for user
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)  # Foreign key for room
    start_date = db.Column(db.DateTime, default=datetime.utcnow)  # Default to current datetime
    end_date = db.Column(db.DateTime, default=datetime.utcnow)   # Default to current datetime
