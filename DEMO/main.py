from flask import Flask

app = Flask(__name__)


@app.route('/')
def home():
    return "Welcome to the home page!"

@app.route('/<text>')
def text(text):
    try:
        text = float(text)
        return "It's a number"
    except:
        return "It's not a number"

if __name__ == '__main__':
    app.run(debug=True)