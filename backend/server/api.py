from bottle import Bottle, request, response
import json
from rpid.api import APIData
from server import user


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


@app.route('/user', method=['GET'])
def act():
    return json.dumps(user.get())

@app.route('/user', method=['POST'])
def act():
    user.create(request.json['name'])
    return response

@app.route('/user', method=['DELETE'])
def act():
    user.delete(request.json['name'])
    return response

@app.route('/stop', method=['OPTIONS', 'POST'])
def act():
    data.deactivate()

@app.route('/start', method=['OPTIONS', 'POST'])
def act():
    data.activate()

@app.route('/program', method=['GET'])
def act():
    return json.loads(data.program) or {}

@app.route('/program', method=['POST'])
def act():
    data.set_program(request.json)
    data.activate()

@app.route('/current', method=['OPTIONS', 'GET'])
def current():
    current_temp = data.current_temp or "n/a"
    current_setting = "%0.2f&deg;C" % float(data.current_setting) if data.current_setting is not None else "off"
    next_steps = data.next_steps or ["---"]
    times_until = data.times_until or ["---"]
    try:
        time_left = data.time_left
    except TypeError:
        time_left = None
    out = {"setting": current_setting,
            "temp": str(current_temp) + " &deg;C",
            "time_left": time_left or "n/a",
            "next_steps": next_steps,
            "times_until": times_until}
    return out
