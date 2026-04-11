from flask import Flask

app = Flask(__name__)
@app.route('/')
def hello():
    return 'Hello WAP!'

app.run(port=5000, host='127.0.0.1')