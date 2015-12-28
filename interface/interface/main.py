import redis
import json


class APIInterface(redis.StrictRedis):
    def clear(self):
        """
        Resets all data, essentially stopping the current program and going back into a state where we're waiting
        for new instructions from the user.

        """
        labels = ["current_temp",
                  "current_step",
                  "time_left",
                  "active",
                  "program",
                  "mode",
                  "next_steps",
                  "times_until"]
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
