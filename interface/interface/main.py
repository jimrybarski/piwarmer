import redis
import json


class APIInterface(redis.StrictRedis):
    def clear(self):
        """
        Resets all data, essentially stopping the current program and going back into a state where we're waiting
        for new instructions from the user.

        """
        labels = ["current_temp",
                  "target_temp",
                  "current_step",
                  "step_time_remaining",
                  "program_time_remaining",
                  "active",
                  "program",
                  "mode",
                  "skip_time"]
        for label in labels:
            self.delete(label)

    def deactivate(self):
        """
        The controller will stop running any programs and will deactivate the heater when this is run.

        """
        self.set("active", 0)

    def activate(self):
        """
        The controller will attempt to start running a program when this is run.

        """
        self.set("active", 1)

    @property
    def step_time_remaining(self):
        """
        The time in seconds until the next step.

        :rtype:     int

        """
        return self.get("step_time_remaining")

    @step_time_remaining.setter
    def step_time_remaining(self, value):
        self.set("step_time_remaining", value)

    @property
    def program_time_remaining(self):
        """
        The time in seconds until the program is over.

        :rtype:     int

        """
        return self.get("program_time_remaining")

    @program_time_remaining.setter
    def program_time_remaining(self, value):
        self.set("program_time_remaining", value)

    @property
    def program(self):
        """
        Gets the currently-loaded program.

        :rtype:     dict

        """
        return json.loads(self.get("program") or "{}")

    @program.setter
    def program(self, value):
        """
        Tell the controller which program to run. It will not start unless activate() is also called.

        :type value:    dict

        """
        self.set("program", value)

    @property
    def driver(self):
        """
        Get the PID values needed for the thing we're heating.

        :rtype:     dict

        """
        return json.loads(self.get("driver"))

    @driver.setter
    def driver(self, value):
        """
        Set the PID values.

        :type value:    dict
        """
        self.set("driver", json.dumps(value))

    @property
    def active(self):
        """
        Whether we are currently running a program.

        :rtype:     bool

        """
        # Redis stores all values as strings
        return self.get("active") == "1"

    @property
    def current_temp(self):
        """
        The last reading taken from the thermometer, in Celsius.

        :rtype:     float

        """
        return self.get("current_temp")

    @current_temp.setter
    def current_temp(self, temp):
        """
        Update the record of the last temperature sensed by the thermometer.

        :type temp:     float
        """
        self.set("current_temp", temp)

    @property
    def target_temp(self):
        """
        The temperature we want the heater to be at, in Celsius.

        :rtype:     float

        """
        return self.get("target_temp")

    @target_temp.setter
    def target_temp(self, temp):
        """
        Update the temperature we're trying to achieve.

        :type temp:     float
        """
        self.set("target_temp", temp)

    @property
    def current_step(self):
        """
        The index of the step of the program that the controller is running.

        :rtype:    int

        """
        return self.get("current_step")

    @current_step.setter
    def current_step(self, step):
        """
        Update the index of the step the controller is on.

        :type step:    int

        """
        self.set("current_step", step)

    @property
    def skip_time(self):
        """
        The number of seconds ahead we should skip.

        :return:

        """
        skip_time = self.get("skip_time")
        return int(skip_time) if skip_time is not None else 0

    def skip_step(self):
        """
        Doesn't skip a step directly, but advances the start time by the number of seconds left in the current step.

        :return:
        """
        if self.step_time_remaining is not None:
            self.set("skip_time", self.skip_time + int(self.step_time_remaining))
