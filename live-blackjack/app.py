from flask import Flask
from models.conn import db
from flask_migrate import Migrate

from blueprints.frontend import app as fe_bp
from blueprints.api import app as api_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blackjack.db'

db.init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(fe_bp)
app.register_blueprint(api_bp, url_prefix='/api')

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
