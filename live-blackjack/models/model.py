from models.conn import db

class Player(db.Model):
    id = db.Column(db.String(36), primary_key=True)  # UUID generato lato client (uno per tab)
    name = db.Column(db.String(80), nullable=False)
    score = db.Column(db.Integer, nullable=False, default=0)
    wins = db.Column(db.Integer, nullable=False, default=0)
    draws = db.Column(db.Integer, nullable=False, default=0)
    losses = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'score': self.score,
            'wins': self.wins,
            'draws': self.draws,
            'losses': self.losses,
        }
