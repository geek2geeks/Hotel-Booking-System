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
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default='available')
    price = db.Column(db.Float, nullable=False)
    amenities = db.relationship('Amenity', secondary=room_amenities, backref='rooms')  # Many-to-many relationship
    reservations = db.relationship('Reservation', backref='room', lazy=True)

class Amenity(db.Model):  # New Model for Amenity
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    check_in_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    check_out_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, default=datetime.utcnow)
    # ... any other fields
