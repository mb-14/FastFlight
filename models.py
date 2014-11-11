from datetime import datetime
from app import app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy(app)
class User(db.Model):
    __tablename__ = "users"
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
