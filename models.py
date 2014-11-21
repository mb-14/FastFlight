from datetime import datetime,timedelta
from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy(app)
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer , primary_key=True)
    email = db.Column('email', db.String(20))
    username = db.Column('username', db.String(50))

    def __init__(self, email, username):
        self.email = email
        self.username = username

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def is_active(self):
        return True

    def get_id(self):
        return unicode(self.id)

class City(db.Model):
    __tablename__ = "city"
    id = db.Column(db.Integer , primary_key=True)
    name = db.Column('name', db.String(20))

    def __init__(self, name):
        self.name = name

class Flight(db.Model):
    __tablename__ = "flight"
    id = db.Column(db.Integer , primary_key=True)
    name = db.Column('name', db.String(20))
    max_seats = db.Column('max_seats',db.Integer)
    
    def __init__(self, name, max_seats):
        self.name = name
        self.max_seats = max_seats


class Journey(db.Model):
    __tablename__ = "journey"
    id = db.Column(db.Integer , primary_key=True)
    date_time = db.Column(db.DateTime)   
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'))
    from_city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    to_city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    fare = db.Column(db.Integer)

    def __init__(self, date_time ,from_city_id , to_city_id , flight_id, fare):
        self.date_time = datetime.strptime(date_time, '%d-%m-%Y %I:%M%p')
        self.from_city_id = from_city_id
        self.to_city_id = to_city_id
        self.flight_id = flight_id
        self.fare = fare

    def expired(self):
        today = datetime.now() - timedelta(hours=12)
        return today > self.date_time

    def available(self):
        booked = Book.query.filter_by(journey_id = self.id).count()
        flight = Flight.query.get(self.flight_id)
        return flight.max_seats - booked

class Book(db.Model):
    __tablename__ = "book"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    journey_id = db.Column(db.Integer,db.ForeignKey('journey.id'))
    name = db.Column(db.String(20))
    age = db.Column(db.Integer)

    def __init__(self,user_id,journey_id,name,age):
        self.user_id = user_id
        self.journey_id = journey_id
        self.name = name
        self.age = age
