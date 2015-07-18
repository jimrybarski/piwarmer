from rest_framework import serializers
from rpidapi import models

class ScientistSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Scientist


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Driver


class ProgramSerializer(serializers.ModelSerializer):
    # scientist = serializers.SlugRelatedField(slug_field='scientist', queryset=models.Scientist.objects.all())

    class Meta:
        model = models.Program
        fields = ('steps', 'scientist', 'driver')
