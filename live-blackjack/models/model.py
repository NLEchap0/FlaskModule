# tabelle del database
from models.conn import db


# la riga del giocatore è anche la sua sessione:
# il server assegna l'id, il browser lo memorizza dopo il login
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    score = db.Column(db.Integer, nullable=False, default=0)
    wins = db.Column(db.Integer, nullable=False, default=0)
    draws = db.Column(db.Integer, nullable=False, default=0)
    losses = db.Column(db.Integer, nullable=False, default=0)


# ogni riga è una mano di blackjack, con le carte salvate come JSON
class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='playing')  # playing o finished
    outcome = db.Column(db.String(20))  # win, draw o loss (quando la mano è finita)
    player_hand = db.Column(db.JSON, nullable=False)
    dealer_hand = db.Column(db.JSON, nullable=False)
    deck = db.Column(db.JSON, nullable=False)
