from bottle import Bottle, request, response
import json
from rpid.api import APIData

app = Bottle()
data = APIData()
app.mount('/backend/', app)


@app.hook('after_request')
def enable_cors():
    """
    Deals with some security issues caused by running two sites both on localhost.

    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    response.headers['Content-Type'] = 'application/json'


@app.route('/', method=['OPTIONS', 'GET'])
def status():
    return "The API is running."


@app.route('/stop', method=['OPTIONS', 'POST'])
def act():
    data.deactivate()


@app.route('/start', method=['OPTIONS', 'POST'])
def act():
    data.activate()


@app.route('/program', method=['OPTIONS', 'GET'])
def act():
    return json.loads(data.program) or {}


@app.route('/program', method=['POST'])
def act():
    data.set_program(request.json)
    data.activate()


@app.route('/current', method=['OPTIONS', 'GET'])
def current():
    current_temp = data.current_temp or "n/a"
    current_setting = data.current_setting or "off"
    try:
        time_left = data.time_left
    except TypeError:
        time_left = None
    return {"setting": current_setting,
            "temp": str(current_temp) + " &deg;C",
            "time_left": time_left or "n/a"}
