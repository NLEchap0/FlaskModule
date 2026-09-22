# pagina principale
from flask import Blueprint, render_template

bp = Blueprint('frontend', __name__)


@bp.route("/")
def home():
    return render_template('game.html')
