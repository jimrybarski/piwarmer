from bottle import Bottle, request, response
import json
from redis import StrictRedis

PORT = 8089
app = Bottle()


@app.hook('after_request')
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
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
        StrictRedis().set("program", str(request.data))
    return {}


@app.route('/stop', method=['OPTIONS', 'POST'])
def act():
    response.headers['Content-Type'] = 'application/json'
    if request.method != 'OPTIONS':
        StrictRedis().delete("program")
    return {}


@app.route('/program', method=['OPTIONS', 'GET'])
def act():
    response.headers['Content-Type'] = 'application/json'
    if request.method == 'OPTIONS':
        return {}
    else:
        return json.loads(StrictRedis().get("program")) or {"1": "No program set."}


@app.route('/current', method=['OPTIONS', 'GET'])
def current():
    response.headers['Content-Type'] = 'application/json'
    if request.method == 'OPTIONS':
        return {}
    else:
        r = StrictRedis()
        current_temp = r.get("current_temp") or "n/a"
        current_setting = r.get("current_setting") or "off"
        minutes_left = r.get("minutes_left")
        minutes_left = "n/a" if minutes_left is None else minutes_left + " minute(s)"
        print("ML %s" % minutes_left)
        data = {"setting": current_setting,
                "temp": str(current_temp) + " &deg;C",
                "minutes_left": minutes_left}
        return data


@app.route('/history', method=['OPTIONS', 'GET'])
def history():
    response.headers['Content-Type'] = 'application/json'
    if request.method == 'OPTIONS':
        return {}
    else:
        keys = StrictRedis().hkeys("history")
        res = {key: "http://localhost:%s/history/%s" % (PORT, key) for key in keys}
        return res


@app.route('/history/<item>', method=['OPTIONS', 'GET'])
def history_csv(item):
    response.headers['Content-Type'] = 'application/text'
    if request.method == 'OPTIONS':
        return {}
    else:
        values = json.loads(StrictRedis().hget("history", item))
        history = ["%s\t%s" % (timestamp, temperature) for timestamp, temperature in sorted(values.items())]
        return "timestamp\ttemperature\n" + "\n".join(history)

app.run(host="0.0.0.0", port=PORT)