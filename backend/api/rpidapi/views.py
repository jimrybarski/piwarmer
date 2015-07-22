import json
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from . import serializers, models
from interface import APIData


class ScientistViewset(ModelViewSet):
    serializer_class = serializers.ScientistSerializer
    queryset = models.Scientist.objects.all()


class DriverViewset(ModelViewSet):
    serializer_class = serializers.DriverSerializer
    queryset = models.Driver.objects.all()


class ProgramViewset(ModelViewSet):
    serializer_class = serializers.ProgramSerializer

    def get_queryset(self):
        if 'user' in self.request.query_params.keys():
            return models.Program.objects.filter(scientist=self.request.query_params['user'])
        return models.Program.objects.all()


class StartView(APIView):
    def post(self, request, format=None):
        data = APIData()
        try:
            driver = models.Driver.objects.get(id=request.data['driver'])
            json_driver = serializers.DriverSerializer(driver)
            data.driver = json_driver.data

            program = models.Program.objects.get(id=request.data['program'])
            json_program = serializers.ProgramSerializer(program)
            data.program = json_program.data['steps']
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": e.message})
        else:
            data.activate()
        return Response(status=status.HTTP_200_OK)


class StopView(APIView):
    def post(self, request, format=None):
        data = APIData()
        data.deactivate()
        data.clear()
        return Response(status=status.HTTP_200_OK)


class CurrentView(APIView):
    def get(self, request, format=None):
        data = APIData()
        current_temp = data.current_temp
        current_setting = "%0.2f&deg;C" % float(data.current_setting) if data.current_setting is not None else "off"
        next_steps = data.next_steps or ["---"]
        times_until = data.times_until or ["---"]
        try:
            time_left = data.time_left
        except TypeError:
            time_left = None
        out = {"setting": current_setting,
               "temp": str(current_temp) + " &deg;C" if current_temp else "---",
               "time_left": time_left or "---",
               "next_steps": next_steps,
               "times_until": times_until}
        return Response(out, status=status.HTTP_200_OK)