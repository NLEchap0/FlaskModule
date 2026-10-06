# test sull'interfaccia: pagine, pulsanti e dati mostrati al giocatore
from models.conn import db
from models.model import Game, Player


# entra al tavolo e restituisce l'id del giocatore
def join(client, app, name):
    client.post('/join', data={'name': name})
    with app.app_context():
        return db.session.scalars(
            db.select(Player).where(Player.name == name)
        ).first().id


# avvia una mano e ritenta se il giocatore fa 21 subito (la mano si chiude da sola)
def start_playing_hand(client, app, player_id):
    for _ in range(10):
        client.post('/new')
        with app.app_context():
            hand = db.session.scalars(
                db.select(Game)
                .filter_by(player_id=player_id)
                .order_by(Game.id.desc())
            ).first()
            if hand and hand.status == 'playing':
                return hand
    raise AssertionError('nessuna mano in corso dopo 10 tentativi')


def test_schermata_di_ingresso(client):
    body = client.get('/').get_data(as_text=True)
    assert 'Benvenuto al tavolo' in body
    assert 'Prendi posto' in body
    assert 'Classifica' not in body


def test_tavolo_dopo_il_join(client, app):
    join(client, app, 'Carol')
    body = client.get('/').get_data(as_text=True)
    assert 'ROYAL BLACKJACK' in body
    assert 'Classifica' in body
    assert 'Il tuo punteggio' in body


def test_legenda_punti_da_score_delta(client, app):
    join(client, app, 'Carol')
    body = client.get('/').get_data(as_text=True)
    assert 'Vittoria +10' in body
    assert 'Pareggio +0' in body
    assert 'Perdita \u221210' in body


def test_carte_visibili_dopo_nuova_mano(client, app):
    player_id = join(client, app, 'Carol')
    start_playing_hand(client, app, player_id)
    body = client.get('/').get_data(as_text=True)
    assert 'data-corner' in body
    assert 'BANCO' in body
    assert 'TU' in body


def test_pulsanti_durante_la_mano(client, app):
    player_id = join(client, app, 'Carol')
    start_playing_hand(client, app, player_id)
    body = client.get('/').get_data(as_text=True)

    # la nuova mano è bloccata mentre si gioca
    assert '<button class="btn btn-gold" disabled>' in body
    # carta e stand sono attivi
    assert '<button class="btn" disabled>' not in body


def test_pulsanti_dopo_aver_perso_o_vinto(client, app):
    player_id = join(client, app, 'Carol')
    start_playing_hand(client, app, player_id)
    client.post('/stand')
    body = client.get('/').get_data(as_text=True)

    # con la mano chiusa carta e stand sono bloccati
    assert '<button class="btn" disabled>' in body
    # il risultato è mostrato con la classe relativa all'esito
    assert 'rb-win' in body or 'rb-draw' in body or 'rb-loss' in body


def test_classifica_con_i_giocatori(client, app):
    join(client, app, 'Carol')
    body = client.get('/').get_data(as_text=True)
    assert 'Giocatore' in body
    assert 'Carol' in body
