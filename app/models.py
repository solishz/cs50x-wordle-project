from . import db
from datetime import datetime, timezone, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Define Iran's timezone (UTC+3:30)
iran_timezone = timezone(timedelta(hours=3, minutes=30))

class Player(db.Model, UserMixin):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    scores = db.relationship('Score', backref='player', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False, default=0)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
