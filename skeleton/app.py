from flask import Flask

from blueprints.frontend import app as fe_bp

app = Flask(__name__)

app.register_blueprint(fe_bp)

if __name__ == "__main__":
    app.run(debug=True)
