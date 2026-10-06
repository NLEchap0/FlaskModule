# route della pagina: ogni azione viene fatta con un form HTML
# e poi si torna sempre sulla pagina principale con un redirect
from flask import Blueprint, render_template, request, redirect, url_for, session
from sqlalchemy import func

from models.conn import db
from models.model import Player, Game
from modules.game import (
    SCORE_DELTA,
    active_game,
    game_data,
    start_game,
    player_draws,
    player_stands,
)

bp = Blueprint('frontend', __name__)


# legge il giocatore salvato nella sessione del browser (se c'è)
def current_player():
    player_id = session.get('player_id')
    if not player_id:
        return None
    return db.session.get(Player, player_id)


# pagina principale: form di ingresso oppure tavolo di gioco
@bp.route("/")
def home():
    player = current_player()

    data = None
    if player:
        # mostra l'ultima mano: quella in corso oppure l'ultima finita
        last = db.session.scalars(
            db.select(Game).filter_by(player_id=player.id).order_by(Game.id.desc())
        ).first()
        if last:
            data = game_data(last)

    players = db.session.scalars(db.select(Player).order_by(Player.score.desc())).all()
    return render_template('game.html', player=player, data=data, players=players,
                           score_delta=SCORE_DELTA)


# login: se il nome è nuovo crea il giocatore, altrimenti rientra con quello vecchio
@bp.route('/join', methods=['POST'])
def join():
    name = (request.form.get('name') or '').strip()
    if not name:
        name = 'Guest'

    # i nomi non distinguono le maiuscole dalle minuscole
    player = db.session.scalars(
        db.select(Player).where(func.lower(Player.name) == name.lower())
    ).first()
    if not player:
        player = Player(name=name)
        db.session.add(player)
        db.session.commit()

    session['player_id'] = player.id
    return redirect(url_for('frontend.home'))


# inizia una nuova mano
@bp.route('/new', methods=['POST'])
def new_game():
    player = current_player()
    if player:
        start_game(player)
    return redirect(url_for('frontend.home'))


# il giocatore chiede una carta
@bp.route('/hit', methods=['POST'])
def hit():
    player = current_player()
    if player:
        hand = active_game(player.id)
        if hand:
            player_draws(hand)
    return redirect(url_for('frontend.home'))


# il giocatore si ferma
@bp.route('/stand', methods=['POST'])
def stand():
    player = current_player()
    if player:
        hand = active_game(player.id)
        if hand:
            player_stands(hand)
    return redirect(url_for('frontend.home'))


# il giocatore lascia il tavolo: chiude la sessione, la scheda resta salvata
@bp.route('/leave', methods=['POST'])
def leave():
    session.pop('player_id', None)
    return redirect(url_for('frontend.home'))
