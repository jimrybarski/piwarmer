from rest_framework import serializers
from rpidapi import models

class ScientistSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Scientist


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Driver


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Program
        fields = ('name', 'steps', 'scientist', 'driver')
