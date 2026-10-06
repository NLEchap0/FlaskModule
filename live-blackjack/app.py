# file principale: crea l'app Flask, collega il database e avvia il server
import os

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate

from models.conn import db
from blueprints.frontend import bp as frontend_bp

# legge le variabili dal file .env, se presente (vedi .env-example)
load_dotenv()

app = Flask(__name__)

# configurazione: in produzione entrambe le variabili vengono da .env
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI', 'sqlite:///blackjack.db'
)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'blackjack-super-segreto')

db.init_app(app)
Migrate(app, db)
app.register_blueprint(frontend_bp)

if __name__ == "__main__":
    app.run(debug=True)
