from django.db import models


class Scientist(models.Model):
    name = models.CharField(max_length=64)


class Driver(models.Model):
    name = models.CharField(max_length=255)
    kp = models.FloatField(default=0.0)
    ki = models.FloatField(default=0.0)
    kd = models.FloatField(default=0.0)
    max_accumulated_error = models.FloatField(default=10.0)
    min_accumulated_error = models.FloatField(default=-10.0)
    max_power = models.FloatField(default=1.0)


class Program(models.Model):
    steps = models.TextField()
    scientist = models.ForeignKey(Scientist)
    driver = models.ForeignKey(Driver)
