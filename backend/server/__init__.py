from bottle import Bottle, request, response
import json
from rpid import Data

PORT = 8089
app = Bottle()
data = Data()
app.mount('/api/', app)


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


@app.route('/start', method=['OPTIONS', 'POST'])
def act():
    response.headers['Content-Type'] = 'application/json'
    if request.method != 'OPTIONS':
        data.activate()
    return {}


@app.route('/stop', method=['OPTIONS', 'POST'])
def act():
    response.headers['Content-Type'] = 'application/json'
    if request.method != 'OPTIONS':
        data.deactivate()
    return {}


@app.route('/program', method=['OPTIONS', 'GET'])
def act():
    response.headers['Content-Type'] = 'application/json'
    if request.method == 'OPTIONS':
        return {}
    else:
        return json.loads(data.program) or {}


@app.route('/program', method=['POST'])
def act():
    response.headers['Content-Type'] = 'application/json'
    if request.method == 'OPTIONS':
        return {}
    else:
        data.set_program(request.data)


@app.route('/current', method=['OPTIONS', 'GET'])
def current():
    response.headers['Content-Type'] = 'application/json'
    if request.method == 'OPTIONS':
        return {}
    else:
        current_temp = data.current_temp or "n/a"
        current_setting = data.current_setting or "off"
        minutes_left = data.minutes_left
        minutes_left = "n/a" if minutes_left is None else minutes_left + " minute(s)"
        return {"setting": current_setting,
                "temp": str(current_temp) + " &deg;C",
                "minutes_left": minutes_left}


@app.route('/history', method=['OPTIONS', 'GET'])
def history():
    response.headers['Content-Type'] = 'application/json'
    if request.method == 'OPTIONS':
        return {}
    else:
        res = {key: "http://localhost:%s/history/%s" % (PORT, key) for key in data.run_times}
        return res


@app.route('/history/<item>', method=['OPTIONS', 'GET'])
def history_csv(item):
    response.headers['Content-Type'] = 'application/text'
    if request.method == 'OPTIONS':
        return {}
    else:
        values = json.loads(data.get_history(item))
        history = ["%s\t%s" % (timestamp, temperature) for timestamp, temperature in sorted(values.items())]
        return "timestamp\ttemperature\n" + "\n".join(history)

app.run(host="127.0.0.1", port=PORT)