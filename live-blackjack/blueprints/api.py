from flask import Blueprint, Response, request, jsonify
from models.conn import db
from models.model import Player
from modules.game import (new_deck, hand_value, dealer_play,
                          resolve_outcome, outcome_to_dict)
from modules import events

app = Blueprint('api', __name__)

# stato di gioco in memoria: session_id -> {'deck', 'player_hand', 'dealer_hand'}
_games = {}


def _get_game(session_id):
    return _games.get(session_id)


def _start_game(session_id):
    deck = new_deck()
    player = [deck.pop(), deck.pop()]
    dealer = [deck.pop()]
    game = {'deck': deck, 'player_hand': player, 'dealer_hand': dealer}
    _games[session_id] = game
    return game


@app.route('/players', methods=['POST'])
def register_player():
    data = request.get_json(silent=True) or {}
    session_id = data.get('session_id')
    name = (data.get('name') or 'Guest').strip() or 'Guest'
    if not session_id:
        return jsonify({'error': 'session_id required'}), 400

    player = db.session.get(Player, session_id)
    if not player:
        player = Player(id=session_id, name=name, score=0)
        db.session.add(player)
        db.session.commit()
        events.broadcast('player_joined', player.to_dict())
    return jsonify(player.to_dict()), 201


@app.route('/players', methods=['GET'])
def list_players():
    players = Player.query.order_by(Player.score.desc()).all()
    return jsonify([p.to_dict() for p in players])


@app.route('/players/leave', methods=['POST'])
def leave_player():
    data = request.get_json(silent=True) or {}
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({'error': 'session_id required'}), 400

    player = db.session.get(Player, session_id)
    if player:
        db.session.delete(player)
        db.session.commit()
        events.broadcast('player_left', {'id': session_id})
    _games.pop(session_id, None)
    return jsonify({'ok': True})


@app.route('/game/new', methods=['POST'])
def new_game():
    data = request.get_json(silent=True) or {}
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({'error': 'session_id required'}), 400
    if not db.session.get(Player, session_id):
        return jsonify({'error': 'player not registered'}), 404

    game = _start_game(session_id)
    return jsonify({
        'player_hand': game['player_hand'],
        'dealer_hand': game['dealer_hand'],
        'player_value': hand_value(game['player_hand']),
        'dealer_value': hand_value(game['dealer_hand']),
        'status': 'playing',
    })


@app.route('/game/hit', methods=['POST'])
def hit():
    data = request.get_json(silent=True) or {}
    session_id = data.get('session_id')
    game = _get_game(session_id)
    if not game:
        return jsonify({'error': 'no active game'}), 404

    game['player_hand'].append(game['deck'].pop())
    pv = hand_value(game['player_hand'])

    if pv > 21:
        return _finish(session_id, game)
    return jsonify({
        'player_hand': game['player_hand'],
        'dealer_hand': game['dealer_hand'],
        'player_value': pv,
        'dealer_value': hand_value(game['dealer_hand']),
        'status': 'playing',
    })


@app.route('/game/stand', methods=['POST'])
def stand():
    data = request.get_json(silent=True) or {}
    session_id = data.get('session_id')
    game = _get_game(session_id)
    if not game:
        return jsonify({'error': 'no active game'}), 404

    dealer_play(game['dealer_hand'], game['deck'])
    return _finish(session_id, game)


def _finish(session_id, game):
    outcome = resolve_outcome(game['player_hand'], game['dealer_hand'])
    info = outcome_to_dict(game['player_hand'], game['dealer_hand'], outcome)

    player = db.session.get(Player, session_id)
    if player:
        player.score = max(0, player.score + info['delta'])
        if outcome == 'win':
            player.wins += 1
        elif outcome == 'loss':
            player.losses += 1
        else:
            player.draws += 1
        db.session.commit()

        result = dict(info)
        result['player'] = player.to_dict()
        events.broadcast('game_result', result)

    _games.pop(session_id, None)

    return jsonify({
        'player_hand': game['player_hand'],
        'dealer_hand': game['dealer_hand'],
        'player_value': info['player_value'],
        'dealer_value': info['dealer_value'],
        'status': 'finished',
        'outcome': info['outcome'],
        'delta': info['delta'],
        'player': player.to_dict() if player else None,
    })


@app.route('/events')
def sse_events():
    q = events.subscribe()

    def stream():
        try:
            while True:
                try:
                    msg = q.get(timeout=15)
                    yield events.format_sse(msg)
                except Exception:
                    # keep-alive per evitare timeout della connessione
                    yield ": keep-alive\n\n"
        finally:
            events.unsubscribe(q)

    return Response(stream(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache',
                             'X-Accel-Buffering': 'no'})
