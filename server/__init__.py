from bottle import Bottle, request, response, run

app = Bottle()


@app.hook('after_request')
def cors():
    response.headers['Access-Control-Allow-Origin'] = '*'


@app.get('/')
def show():
    return {"lulz": True}


@app.post('/act')
def act():
    return request.body


app.run(host="0.0.0.0", port=8089)