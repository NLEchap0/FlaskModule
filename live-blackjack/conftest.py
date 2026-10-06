# fixture condivise da tutti i test: app di test su un database in memoria
import os

# va impostato prima di importare app: così i test non toccano il db reale
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

import pytest

from app import app as flask_app
from models.conn import db


# ogni test parte da uno schema pulito e lo elimina alla fine
@pytest.fixture()
def app():
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()


# client HTTP per le richieste di test
@pytest.fixture()
def client(app):
    return app.test_client()


# crea un giocatore e ne restituisce l'id
@pytest.fixture()
def player_id(app, client):
    from models.model import Player

    client.post('/join', data={'name': 'Alice'})
    with app.app_context():
        return db.session.scalars(
            db.select(Player).where(Player.name == 'Alice')
        ).first().id
