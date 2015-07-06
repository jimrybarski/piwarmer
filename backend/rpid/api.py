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
        labels = ["current_temp", "current_setting", "active", "program", "mode", "seconds_left", "next_steps", "time_until"]
        for label in labels:
            self.delete(label)

    def update_temperature(self, temp):
        self.set("current_temp", temp)

    def update_setting(self, desired_temp):
        self.set("current_setting", desired_temp)

    def update_next_steps(self, next_steps):
        current_steps_count = self.llen('next_steps')
        # update the steps with current data
        for n, (time_until, step) in enumerate(next_steps):
            self.lpush('next_steps', step.message)
            self.lpush('times_until', time_until)
        # remove any old steps that are now at the end of the list
        for _ in range(current_steps_count):
            self.rpop('next_steps')
            self.rpop('times_until')

    @property
    def next_steps(self):
        return [step for step in self.lrange('next_steps', 0, -1) or []]

    @property
    def times_until(self):
        return [time_until for time_until in self.lrange('times_until', 0, -1) or []]

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
    def time_left(self):
        return self.get("time_left")

    @time_left.setter
    def time_left(self, value):
        self.set("time_left", value)
