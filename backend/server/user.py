import os
from server import DATA_PATH

def get():
    return [name for name in os.listdir(DATA_PATH + '/user')]


def create(username):
    path = DATA_PATH + '/user/%s' % username
    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except (OSError, SystemError):
            return False
        else:
            return True
    # user already exists
    return True

def delete(username):
    path = DATA_PATH + '/user/%s' % username
    if not os.path.isdir(path):
        # already deleted
        return True
    try:
        os.rmdir(path)
    except (OSError, SystemError):
        return False
    else:
        return True
