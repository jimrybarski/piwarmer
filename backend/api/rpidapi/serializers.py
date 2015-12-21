"""
This just automatically builds out the serialization of each object in the database,
so that Javascript can interact with the API using JSON.

"""
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
        fields = ('id', 'name', 'steps', 'scientist', 'driver')
