from django.db import models


# Users
class Scientist(models.Model):
    name = models.CharField(max_length=64)


# PID values for different heating blocks
class Driver(models.Model):
    name = models.CharField(max_length=255)
    kp = models.FloatField(default=0.0)
    ki = models.FloatField(default=0.0)
    kd = models.FloatField(default=0.0)
    max_accumulated_error = models.FloatField(default=10.0)
    min_accumulated_error = models.FloatField(default=-10.0)
    max_power = models.FloatField(default=1.0)


# A set of instructions for heating something at given temperatures for a given amount of time
class Program(models.Model):
    name = models.CharField(max_length=128)
    steps = models.TextField()
    scientist = models.ForeignKey(Scientist)
    driver = models.ForeignKey(Driver)
