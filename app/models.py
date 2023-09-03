from datetime import datetime
from app import db, bcrypt


room_amenities = db.Table('room_amenities',
    db.Column('room_id', db.Integer, db.ForeignKey('room.id')),
    db.Column('amenity_id', db.Integer, db.ForeignKey('amenity.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)  # Added is_admin column
    reservations = db.relationship('Reservation', backref='guest', lazy=True)

    @property
    def is_active(self):
        # Here, you can add more complex logic if needed, 
        # like checking if a user is banned, etc.
        return True

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)



class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    amenities = db.relationship('Amenity', secondary=room_amenities, backref='rooms')
    bookings = db.relationship('Booking', backref='room', lazy=True)  # changed from reservations to bookings
    
    @property
    def status(self):
        # If there's an active booking, set the status to occupied, else available
        for booking in self.bookings:
            if booking.start_date <= datetime.utcnow() <= booking.end_date:
                return 'occupied'
        return 'available'

class Amenity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, default=datetime.utcnow)



