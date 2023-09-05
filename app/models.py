# app/models.py

from datetime import datetime
from app.extensions import db, bcrypt  
from enum import Enum
from flask_login import UserMixin
from datetime import timedelta

class RoomType(Enum):
    SINGLE = "SINGLE"
    DOUBLE = "DOUBLE"

room_amenities = db.Table('room_amenities',
    db.Column('room_id', db.Integer, db.ForeignKey('room.id')),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenity.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    bookings = db.relationship('Booking', backref='guest', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(50), nullable=False)
    type = db.Column(db.Enum(RoomType), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    amenities = db.relationship('Amenity', secondary=room_amenities, backref='rooms')
    bookings = db.relationship('Booking', backref='room', lazy=True)

    @property
    def status(self):
        return 'occupied' if self.is_occupied(datetime.utcnow()) else 'available'

    def is_occupied(self, date):
        """
        Check if the room is occupied on a given date.
        :param date: Date to check.
        :return: Boolean indicating if room is occupied.
        """
        for booking in self.bookings:
            if booking.start_date <= date <= booking.end_date:
                return True
        return False
    
    def is_available(self, check_in_date, check_out_date):
        """
        Check if the room is available for a given date range.
        :param check_in_date: Start date for checking availability.
        :param check_out_date: End date for checking availability.
        :return: Boolean indicating if room is available.
        """
        for booking in self.bookings:
            # If there's any overlap between the desired date range and any of the booking date ranges,
            # the room is not available.
            if not (booking.end_date < check_in_date or booking.start_date > check_out_date):
                return False
        return True
    
    @property
    def amenities_list(self):
        """
        Return amenities of the room as a comma-separated string.
        """
        return ', '.join([amenity.name for amenity in self.amenities])

class Amenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    total_price = db.Column(db.Float)

    def calculate_total_price(self):
        """
        Calculate the total price based on the number of days and room price.
        Ensure the associated room is present before attempting the calculation.
        """
        if not self.room:
            raise ValueError("Booking has no associated room!")
        num_days = (self.end_date - self.start_date).days
        self.total_price = num_days * self.room.price
        # Optionally, if you want to automatically save this to the database after calculating:
        db.session.add(self)
        db.session.commit()

    @db.validates('start_date', 'end_date')
    def validate_dates(self, key, date):
        if key == "start_date" and date >= self.end_date:
            raise ValueError("Start date must be before end date")
        elif key == "end_date" and date <= self.start_date:
            raise ValueError("End date must be after start date")
        return date

    @db.after_insert
    def _after_insert(self):
        """
        After a booking is inserted into the database, calculate its total price.
        """
        self.calculate_total_price()

    @db.after_update
    def _after_update(self):
        """
        After a booking is updated in the database, recalculate its total price.
        """
        self.calculate_total_price()