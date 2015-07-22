import redis
import json
import logging

log = logging.getLogger()

TEN_MINUTES = 600  # seconds


class APIData(redis.StrictRedis):
    def clear(self):
        """
        Resets everything.

        """
        labels = ["current_temp", "current_setting", "active", "program", "mode", "next_steps", "times_until"]
        for label in labels:
            self.delete(label)

    def update_temperature(self, temp):
        self.set("current_temp", temp)

    def update_setting(self, desired_temp):
        self.set("current_setting", desired_temp)

    def update_next_steps(self, next_steps, times_until):

        # in case there's a request for this data while we're deleting the old records,
        # we start from the end so that we never send back anything inconsistent
        for n in range(5 - len(next_steps)):
            self.hdel('next_steps', 4 - n)
            self.hdel('times_until', 4 - n)
        # race condition here. it won't affect anything but it may be surprising to the user that the times are off for one
        # second. if we want this to be truly bulletproof we need to implement a mutex or something similar.
        # it may be fast enough that errors will just never be visible
        self.hmset('next_steps', next_steps)
        self.hmset('times_until', times_until)

    @property
    def next_steps(self):
        ns = self.hgetall('next_steps')
        return ns

    @property
    def times_until(self):
        return self.hgetall('times_until')

    def deactivate(self):
        self.set("active", 0)
        self.delete("program")

    def activate(self):
        self.set("active", 1)

    @property
    def program(self):
        return json.loads(self.get("program"))

    @program.setter
    def program(self, value):
        self.set("program", value)

    @property
    def driver(self):
        return json.loads(self.get("driver"))

    @driver.setter
    def driver(self, value):
        self.set("driver", json.dumps(value))

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
    def time_left(self):
        return self.get("time_left")

    @time_left.setter
    def time_left(self, value):
        self.set("time_left", value)

