# test di isolamento: ogni giocatore agisce solo sulle proprie mani
from models.conn import db
from models.model import Game, Player


# secondo giocatore, con sessione indipendente
def join_second(app, name):
    other = app.test_client()
    other.post('/join', data={'name': name})
    return other


def count_games(app, player_id):
    with app.app_context():
        return len(db.session.scalars(
            db.select(Game).filter_by(player_id=player_id)
        ).all())


def test_mano_di_un_giocatore_non_appare_all_altro(app, client, player_id):
    other = join_second(app, 'Bob')
    client.post('/new')

    # Bob non ha mani e la pagina non mostra nessuna carta
    body = other.get('/').get_data(as_text=True)
    assert 'data-corner' not in body
    assert count_games(app, player_id) == 1


def test_le_azioni_di_un_giocatore_non_touchano_l_altro(app, client, player_id):
    other = join_second(app, 'Bob')
    with app.app_context():
        bob_id = db.session.scalars(
            db.select(Player).where(Player.name == 'Bob')
        ).first().id

    client.post('/new')
    client.post('/hit')
    client.post('/stand')

    # Bob resta a zero: né mani né punteggio
    assert count_games(app, bob_id) == 0
    with app.app_context():
        assert db.session.get(Player, bob_id).score == 0


def test_le_azioni_senza_mano_non_rubano_le_altre_mani(app, client, player_id):
    other = join_second(app, 'Bob')
    client.post('/new')

    with app.app_context():
        hand = db.session.scalars(
            db.select(Game).filter_by(player_id=player_id)
        ).first()
        before = (hand.status, list(hand.player_hand), list(hand.dealer_hand))

    # Bob prova a pescare e a fermarsi senza avere una mano
    other.post('/hit')
    other.post('/stand')

    with app.app_context():
        hand = db.session.scalars(
            db.select(Game).filter_by(player_id=player_id)
        ).first()
        after = (hand.status, list(hand.player_hand), list(hand.dealer_hand))
    assert after == before


def test_punteggi_indipendenti(app, client, player_id):
    other = join_second(app, 'Bob')
    with app.app_context():
        bob_id = db.session.scalars(
            db.select(Player).where(Player.name == 'Bob')
        ).first().id

    client.post('/new')
    client.post('/stand')

    with app.app_context():
        # la mano di Alice è chiusa, quella di Bob non esiste
        alice_hand = db.session.scalars(
            db.select(Game).filter_by(player_id=player_id)
        ).first()
        assert alice_hand.status == 'finished'
        assert db.session.get(Player, bob_id).score == 0
        assert db.session.get(Player, bob_id).wins == 0
        assert db.session.get(Player, bob_id).losses == 0
