from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize SQLAlchemy instance
db = SQLAlchemy()

login_manager = LoginManager()
# Redirects to the login page if unauthorized
login_manager.login_view = 'login'



# Set up the app
app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wordle.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database with the app
db.init_app(app)

login_manager.init_app(app)

# Import models so they are registered with SQLAlchemy
from .models import Player, Score

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Disable browser caching
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@login_manager.user_loader
def load_user(user_id):
    return Player.query.get(int(user_id))  # Retrieve the user by ID

def reset_scores():
    with app.app_context():
        # Set all scores to zero
        Score.query.update({Score.score: 0})
        db.session.commit()

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Schedule the reset to run every day at midnight
    scheduler.add_job(reset_scores, 'cron', hour=0, minute=0)
    scheduler.start()

start_scheduler()

# Import routes after app is created to avoid circular imports
from app import routes
