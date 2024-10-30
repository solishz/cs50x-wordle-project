import os
from app import app
from flask import render_template, request, jsonify, session, url_for, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
from .models import Player, Score
from . import db
from sqlalchemy import desc, func
from app.helpers import is_word_valid, get_random_word

# Initialize the secret key for session management
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

@app.route('/', methods=["GET"])
def index():
    """ Main page """
    if request.args.get("start") == "1":
        # User clicked on the start button
        return redirect(url_for('wordle'))
    
    return render_template('wordle.html')

@app.route('/wordle', methods=["GET"])
@login_required
def wordle():
    """ Wordle game page """
    # initialize the game word
    session['game_word'] = get_random_word()
    return render_template('wordle.html', start=True)
    

@app.route('/register', methods=["GET", "POST"])
def register():
    """ Registration page """
    
    # User reaches via method POST
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirmation = request.form['confirmation']
        existing_user = Player.query.filter_by(username=username).first()
        
        if username == "":
            flash('Invalid username')
            return redirect(url_for('register'))
        
        if existing_user:
            flash('Username already exists. Please choose another one.')
            return redirect(url_for('register'))
        
        if not password == confirmation:
            flash('Password and Confirmation must be the same.')
            return redirect(url_for('register'))
        
        if len(password) < 8:
            flash('Password must be atleast 8 characters.')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = Player(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    """ Login page """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Player.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!')
            # Redirect to home page
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
            
    return render_template('login.html')

# Create a separate route for word submission
@app.route('/submit-word', methods=["POST"])
def submit_word():
    """ Handle word submission """
    data = request.get_json()
    
    if data: 
        # Get the submitted word
        word = data.get("word", "").lower()
        score = data.get("score", "")
    
        
        # Check if word is correct
        if word == session["game_word"]:
            # Word is correct
            feedback = ["+" for _ in session["game_word"]]
            # Make sure the score is a valid integer
            try:
                score_value = 70 - int(score) * 10
                if score_value > 60 or score_value < 10:
                    return "Invalid score value", 400
            except ValueError:
                return "Invalid score value", 400
                
            # Query the current user's existing score entry
            existing_score = Score.query.filter_by(player_id=current_user.id).first()

            if existing_score:
                # If a score entry exists, add the new score to the current score
                existing_score.score += score_value
            else:
                # If no score entry exists, create a new one
                existing_score = Score(player_id=current_user.id, score=score_value)

            # Add or update the score in the database
            db.session.add(existing_score)
            db.session.commit()
            
            return jsonify({"result": "correct", "feedback": feedback, "score": score_value})
        elif not is_word_valid(word):
            # Word is not a word
            return jsonify({"result": f"{word} is not a word"})
        else:
            # Word is incorrect
            # find correct and incorrect letters in word
            feedback = []
            a  = [ch for ch in session["game_word"]]
                    
            for i in range(len(a)):
                if (word[i] == a[i]):
                    # Letter is in the correct place
                    feedback.append("+")
                elif (word[i] in a):
                    # Letter is in the incorrect place
                    feedback.append("-")
                else:
                    # Letter is not in the word
                    feedback.append(".")
            print(a)
            print(feedback)
            return jsonify({"result": "incorrect", "feedback": feedback})
    else:
        return jsonify({"error": "No data received"}), 400
    
    
@app.route('/logout')
@login_required
def logout():
    """ Logs out the user """
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/scoreboard', methods=['GET', 'POST'])
def scoreboard():
    """ Shows the table of players and their scores """
    # Query to get players and their scores
    scores = db.session.query(
        func.row_number().over(order_by=Score.score.desc()).label("rank"),
        Player.username,
        Score.score
    ).join(Score).order_by(desc(Score.score)).all()
    if current_user.is_authenticated:
        user_score = db.session.query(Score.score).filter_by(player_id=current_user.id).first()
    else:
        user_score = None
    return render_template('scoreboard.html', scores=scores, user_score=user_score)

@app.route('/how-to-play', methods=["GET"])
def how_to_play():
    """ How to play page """
    return render_template('howtoplay.html')

@app.route('/about', methods=["GET"])
def about():
    """ About page """
    return render_template('about.html')