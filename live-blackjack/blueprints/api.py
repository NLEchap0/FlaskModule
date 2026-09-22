# API del gioco: le route leggono la richiesta, chiamano le funzioni
# di modules/game.py e restituiscono JSON
from flask import Blueprint, Response, request, jsonify
from models.conn import db
from models.model import Player, Game
from modules import game, events

bp = Blueprint('api', __name__)


# login: se il nome è nuovo crea il giocatore, altrimenti rientra nella sua sessione
@bp.route('/players', methods=['POST'])
def register_player():
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    if not name:
        name = 'Guest'

    player = db.session.scalars(db.select(Player).filter_by(name=name)).first()
    if not player:
        player = Player(name=name)
        db.session.add(player)
        db.session.commit()
        events.broadcast('player_joined', player.to_dict())
        return jsonify(player.to_dict()), 201

    return jsonify(player.to_dict()), 200


# classifica con tutti i giocatori
@bp.route('/players', methods=['GET'])
def list_players():
    players = db.session.scalars(db.select(Player).order_by(Player.score.desc())).all()
    return jsonify([p.to_dict() for p in players])


# il giocatore lascia il tavolo (chiamata quando chiude il tab)
@bp.route('/players/leave', methods=['POST'])
def leave_player():
    data = request.get_json(silent=True) or {}
    player = db.session.get(Player, data.get('player_id'))
    if player:
        # cancello anche le sue mani dal database
        db.session.execute(db.delete(Game).filter_by(player_id=player.id))
        db.session.delete(player)
        db.session.commit()
        events.broadcast('player_left', {'id': player.id})
    return jsonify({'ok': True})


# inizia una nuova mano
@bp.route('/game/new', methods=['POST'])
def new_game():
    data = request.get_json(silent=True) or {}
    player = db.session.get(Player, data.get('player_id'))
    if not player:
        return jsonify({'error': 'Player non trovato'}), 404

    return jsonify(game.start_game(player))


# il giocatore chiede una carta
@bp.route('/game/hit', methods=['POST'])
def hit():
    data = request.get_json(silent=True) or {}
    active = game.active_game(data.get('player_id'))
    if not active:
        return jsonify({'error': 'Nessuna mano in corso'}), 404

    return jsonify(game.player_draws(active))


# il giocatore si ferma
@bp.route('/game/stand', methods=['POST'])
def stand():
    data = request.get_json(silent=True) or {}
    active = game.active_game(data.get('player_id'))
    if not active:
        return jsonify({'error': 'Nessuna mano in corso'}), 404

    return jsonify(game.player_stands(active))


# eventi in tempo reale: il browser resta collegato e riceve i messaggi
@bp.route('/events')
def sse_events():
    q = events.subscribe()

    def stream():
        try:
            while True:
                try:
                    msg = q.get(timeout=15)
                    yield events.format_sse(msg)
                except Exception:
                    # messaggio vuoto per tenere viva la connessione
                    yield ": keep-alive\n\n"
        finally:
            events.unsubscribe(q)

    return Response(stream(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache'})
