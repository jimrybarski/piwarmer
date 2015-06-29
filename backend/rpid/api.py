import redis
import json

TEN_MINUTES = 600  # seconds


class APIData(redis.StrictRedis):
    def clear(self):
        """
        Resets everything.

        """
        labels = ["current_temp", "current_setting", "active", "program", "mode", "seconds_left"]
        for label in labels:
            self.delete(label)

    def update_temperature(self, temp):
        self.set("current_temp", temp)

    def update_setting(self, desired_temp):
        self.set("current_setting", desired_temp)

    def deactivate(self):
        self.set("active", 0)
        self.delete("program")

    def activate(self):
        self.set("active", 1)

    @property
    def program(self):
        return self.get("program")

    def set_program(self, program):
        self.set("program", json.dumps(program))

    @property
    def active(self):
        return self.get("active") == "1"

    @property
    def current_temp(self):
        return self.get("current_temp")

    @property
    def current_setting(self):
        return self.get("current_setting")

    @property
    def seconds_left(self):
        return self.get("seconds_left")

    @seconds_left.setter
    def seconds_left(self, value):
        self.set("seconds_left", value)