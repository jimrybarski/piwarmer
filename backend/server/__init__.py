from bottle import Bottle, request, response
import json
from rpid.api import APIData

app = Bottle()
api_data = APIData()
app.mount('/backend/', app)


@app.hook('after_request')
def enable_cors():
    """
    Deals with some security issues caused by running two sites both on localhost.

    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


@app.route('/', method=['OPTIONS', 'GET'])
def status():
    return "The API is running."


@app.route('/stop', method=['OPTIONS', 'POST'])
def act():
    response.headers['Content-Type'] = 'application/json'
    if request.method != 'OPTIONS':
        api_data.deactivate()
    return {}

@app.route('/start', method=['OPTIONS', 'POST'])
def act():
    response.headers['Content-Type'] = 'application/json'
    if request.method != 'OPTIONS':
        api_data.activate()
    return {}

@app.route('/program', method=['OPTIONS', 'GET'])
def act():
    response.headers['Content-Type'] = 'application/json'
    if request.method == 'OPTIONS':
        return {}
    else:
        return json.loads(api_data.program) or {}


@app.route('/program', method=['POST'])
def act():
    response.headers['Content-Type'] = 'application/json'
    if request.method == 'OPTIONS':
        return {}
    else:
        api_data.set_program(request.json)
        api_data.activate()


@app.route('/current', method=['OPTIONS', 'GET'])
def current():
    response.headers['Content-Type'] = 'application/json'
    if request.method == 'OPTIONS':
        return {}
    else:
        current_temp = api_data.current_temp or "n/a"
        current_setting = api_data.current_setting or "off"
        try:
            seconds_left = api_data.seconds_left
        except TypeError:
            seconds_left = None
        seconds_left = "n/a" if seconds_left is None else seconds_left + " seconds(s)"
        return {"setting": current_setting,
                "temp": str(current_temp) + " &deg;C",
                "seconds_left": seconds_left}
