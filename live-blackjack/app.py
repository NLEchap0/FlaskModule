# file principale: crea l'app Flask, collega il database e avvia il server
import os

from flask import Flask

from models.conn import db
from blueprints.frontend import bp as frontend_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blackjack.db'

# chiave per firmare i cookie di sessione, in produzione va da variabile d'ambiente
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'blackjack-super-segreto')

db.init_app(app)
app.register_blueprint(frontend_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
