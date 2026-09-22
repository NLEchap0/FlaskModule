# file principale: crea l'app Flask, collega il database e avvia il server
from flask import Flask
from flask_migrate import Migrate

from models.conn import db
from blueprints.frontend import bp as frontend_bp
from blueprints.api import bp as api_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blackjack.db'

db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(frontend_bp)
app.register_blueprint(api_bp, url_prefix='/api')

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
