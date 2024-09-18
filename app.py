from flask import Flask, session, render_template, request, jsonify
from boggle import Boggle

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'  # Needed for using sessions
app.static_folder = 'static'  # This ensures Flask serves from the 'static' folder

boggle_game = Boggle()

@app.route("/")
def home():
    """Display the home page with a start game button."""
    return render_template("home.html")

@app.route("/new-game")
def new_game():
    """Generate a new Boggle board and store it in the session."""
    board = boggle_game.make_board()
    session['board'] = board
    return render_template("game.html", board=board)

@app.route("/check-word", methods=["POST"])
def check_word():
    """Check if a submitted word is valid, and return the result as JSON."""
    word = request.json.get("word")
    board = session.get('board')
    result = boggle_game.check_valid_word(board, word)
    return jsonify({'result': result})

@app.route("/post-score", methods=["POST"])
def post_score():
    """Receive the score, update games played, and track the highest score."""
    score = request.json.get("score")
    games_played = session.get('games_played', 0)
    high_score = session.get('high_score', 0)

    session['games_played'] = games_played + 1
    session['high_score'] = max(high_score, score)

    return jsonify({
        "games_played": session['games_played'],
        "high_score": session['high_score']
    })

@app.route("/score", methods=["POST"])
def score():
    """Calculate and return the score based on the words provided."""
    words = request.json['words']
    score = sum(len(word) for word in words)  # Simple scoring by word length
    return jsonify({'score': score})