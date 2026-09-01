from flask import *

app = Flask(__name__)


@app.route('/')
def home():
    return "Welcome to the home page!"

@app.route('/check/<text>')
def text(text):
    try:
        text = float(text)
        return "It's a number"
    except:
        return "It's not a number"

@app.route('/hello/')
@app.route('/hello/<string:inputName>')
def temmplate(inputName = "Are you dumb?"):
    return render_template('hello.html', name=inputName)

if __name__ == '__main__':
    app.run(debug=True)