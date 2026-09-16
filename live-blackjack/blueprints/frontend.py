from flask import Blueprint, render_template

app = Blueprint('frontend', __name__)


@app.route("/")
def home():
    return render_template('game.html')
