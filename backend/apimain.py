from server import *
import time

if __name__ == "__main__":
    time.sleep(330)
    app.run(host="127.0.0.1", port=8089, server='gunicorn', workers=1)
