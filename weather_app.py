import requests
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/")
def home_page():
    response = {
        "oki": 123
    }

    return response


if __name__ == '__main__':
    app.run(port=8000, debug=True)
