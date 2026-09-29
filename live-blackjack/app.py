# file principale: crea l'app Flask, collega il database e avvia il server
from flask import Flask

from models.conn import db
from blueprints.frontend import bp as frontend_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blackjack.db'
app.secret_key = 'blackjack-super-segreto'

db.init_app(app)
app.register_blueprint(frontend_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
