import redis
import json

TEN_MINUTES = 600  # seconds


class APIData(redis.StrictRedis):
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

    def set_mode(self, mode):
        self.set("mode", mode)

    @property
    def manual(self):
        return self.get("mode") == "manual"

    @property
    def minutes_left(self):
        return self.get("minutes_left")

    @minutes_left.setter
    def minutes_left(self, value):
        self.set("minutes_left", value)
