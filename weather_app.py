import datetime as dt
import json

import requests
from flask import Flask, jsonify, request, send_file

API_TOKEN = ""

WEATHER_API_BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services"
WEATHER_API_KEY = ""

APP_URL = 'http://127.0.0.1:8000'

app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


def prepare_weather_url(location: str, date: str):
    return f"{WEATHER_API_BASE_URL}/timeline/{location}/{date}?key={WEATHER_API_KEY}&unitGroup=metric"


def fetch_weather(location: str, date: str):
    response = requests.get(prepare_weather_url(location, date))

    if response.status_code == requests.codes.ok:
        return json.loads(response.text)
    else:
        raise InvalidUsage(response.text, status_code=response.status_code)


def get_utc_timestamp():
    return dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def get_weather_icon_image(icon: str):
    return f"{APP_URL}/api/v1/files/{icon}.svg"


def prepare_weather_data(weather_response):

    return {
        "temp_c": weather_response["days"][0]["temp"],
        "wind_kph": weather_response["days"][0]["windspeed"],
        "pressure": weather_response["days"][0]["pressure"],
        "humidity": weather_response["days"][0]["humidity"],
        "cloudcover": weather_response["days"][0]["cloudcover"],
        "icon_image": get_weather_icon_image(weather_response["days"][0]["icon"]),
    }


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>Weather Saas API</h2></p>"


@app.route("/api/v1/files/<string:filename>", methods=["GET"])
def get_file(filename):
    return send_file(f"./static/weather-icons/{filename}")


@app.route("/api/v1/weather", methods=["GET"])
def weather_controller():
    userPayload = request.args

    if userPayload.get('auth_token') is None or userPayload.get('auth_token') != API_TOKEN:
        raise InvalidUsage("unauthorized", status_code=401)

    requestor_name = userPayload.get('requestor_name')
    location = userPayload.get('location')
    date = userPayload.get('date')

    if location is None or date is None:
        raise InvalidUsage("date and location are required", status_code=401)

    weather_response = fetch_weather(location, date)

    result = {
        "requestor_name": requestor_name,
        "timestamp": get_utc_timestamp(),
        "location": weather_response.get('address'),
        "weather": prepare_weather_data(weather_response),
        "weather_response": weather_response,
    }

    return result


# remove before running on server
if __name__ == '__main__':
    app.run(port=8000, debug=True)
