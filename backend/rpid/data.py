class Data(object):
    """
    Collects data from various sources.

    """
    def __init__(self):
        self._desired_temperature = None
        self._pid_error = None
        self._temperatures = []
        self._active = None
        self._seconds_left = None

