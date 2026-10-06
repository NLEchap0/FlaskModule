# test sulle route: join, gioco, uscita e codici di risposta
from sqlalchemy import func

from models.conn import db
from models.model import Game, Player


def test_home_mostra_form_senza_sessione(client):
    body = client.get('/').get_data(as_text=True)
    assert 'Benvenuto al tavolo' in body


def test_join_crea_giocatore(client, app):
    client.post('/join', data={'name': 'Bob'})
    with app.app_context():
        assert db.session.scalars(
            db.select(Player).where(Player.name == 'Bob')
        ).first() is not None


def test_join_stesso_nome_non_crea_duplicato(client, app):
    client.post('/join', data={'name': 'Bob'})
    client.post('/join', data={'name': 'BOB'})
    with app.app_context():
        count = len(db.session.scalars(
            db.select(Player).where(func.lower(Player.name) == 'bob')
        ).all())
    assert count == 1


def test_join_senza_nome_non_scadica(client, app):
    response = client.post('/join', data={})
    assert response.status_code == 302
    with app.app_context():
        assert db.session.scalars(
            db.select(Player).where(Player.name == 'Guest')
        ).first() is not None


def test_nuova_mano_distribuisce_le_carte(client, app, player_id):
    client.post('/new')
    with app.app_context():
        hand = db.session.scalars(
            db.select(Game).filter_by(player_id=player_id)
        ).first()
        assert hand is not None
        assert len(hand.player_hand) == 2
        assert len(hand.dealer_hand) == 1
        # il mazzo completo è sempre in mano tra carte distribuite e residuo
        assert len(hand.deck) + len(hand.player_hand) + len(hand.dealer_hand) == 52


def test_hit_e_stand_chiudono_la_mano(client, app, player_id):
    client.post('/new')
    client.post('/hit')
    client.post('/stand')
    with app.app_context():
        hand = db.session.scalars(
            db.select(Game).filter_by(player_id=player_id)
        ).first()
        assert hand.status == 'finished'
        assert hand.outcome in ('win', 'draw', 'loss')


def test_leave_conserva_il_giocatore(client, app, player_id):
    client.post('/new')
    client.post('/leave')

    # la sessione è chiusa: torna la schermata di ingresso
    body = client.get('/').get_data(as_text=True)
    assert 'Benvenuto al tavolo' in body

    # ma il giocatore e le sue mani sono ancora lì
    with app.app_context():
        assert db.session.get(Player, player_id) is not None
        assert len(db.session.scalars(
            db.select(Game).filter_by(player_id=player_id)
        ).all()) == 1


def test_rientro_riprende_il_punteggio(client, app, player_id):
    client.post('/new')
    client.post('/stand')
    with app.app_context():
        score_before = db.session.get(Player, player_id).score

    client.post('/leave')
    client.post('/join', data={'name': 'Alice'})
    with app.app_context():
        assert db.session.get(Player, player_id).score == score_before


def test_hit_senza_mano_non_scadica(client):
    assert client.post('/hit').status_code == 302
    assert client.post('/stand').status_code == 302
