from flask_login import UserMixin
from extensions import db

class Admin(db.Model, UserMixin):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def get_id(self):
        return f"admin_{self.id}"

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phonenumber = db.Column(db.String(255), nullable=False)

    def get_id(self):
        return f"user_{self.id}"

class Rooms(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    roomtype = db.Column(db.String(255))
    roomnumber = db.Column(db.String(20), nullable=False, unique = True)
    floor = db.Column(db.Integer)
    hastv = db.Column(db.Boolean)
    haswifi = db.Column(db.Boolean)
    hasminibar = db.Column(db.Boolean)
    pricepernight = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

class Bookings(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'))
    roomid = db.Column(db.Integer, db.ForeignKey('rooms.id'))
    startdate = db.Column(db.Date, nullable=False)
    enddate = db.Column(db.Date, nullable=False)
    totalprice = db.Column(db.Integer)

class Reviews(db.Model):
    __tablename__= 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    bookingid = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    rating = db.Column(db.Integer)
    reviewtext = db.Column(db.String())