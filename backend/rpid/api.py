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

    def update_next_steps(self, next_steps):
        """
        Use a transaction to make this whole step atomic. This is important because we want the API to always
        have data available. We have to delete the "next steps" entirely and rebuild it so that all the data is
        consistent and because at the end there will be fewer than five steps, and this is the easiest way.

        """
        pipe = self.pipeline()
        pipe.delete('next_steps')
        pipe.delete('times_until')
        for n, (time_until, step) in enumerate(next_steps):
            pipe.lset('next_steps', n, step)
            pipe.lset('times_until', n, time_until)
        pipe.execute(False)  # False prevents raising exceptions on error

    @property
    def next_steps(self):
        return [step for step in self.get('next_steps')]

    @property
    def times_until(self):
        return [time_until for time_until in self.get('times_until')]

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
