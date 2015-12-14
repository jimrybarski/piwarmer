from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from . import serializers, models
from interface import APIData
import logging
import os

log = logging.getLogger(__name__)


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
            log.info("Program start requested")
            log.info(str(request.data))
            driver = models.Driver.objects.get(id=request.data['driver'])
            json_driver = serializers.DriverSerializer(driver)
            data.driver = json_driver.data

            program = models.Program.objects.get(id=request.data['program'])
            json_program = serializers.ProgramSerializer(program)
            data.program = json_program.data['steps']
        except Exception as e:
            log.exception("Could not start program")
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": e.message})
        else:
            data.activate()
        log.info("Program started fine")
        return Response(status=status.HTTP_200_OK)


class StopView(APIView):
    def post(self, request, format=None):
        log.info("Stop program requested")
        data = APIData()
        data.deactivate()
        data.clear()
        log.info("Program stopped OK")
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


class TemperatureLogView(APIView):
    def get(self, request, format=None):
        log_dir = "/var/log/piwarmer/"
        if 'date' in self.request.query_params.keys():
            try:
                with open(log_dir + "temperature-%s.log" % self.request.query_params['date']) as f:
                    return Response({n: line.rstrip() for n, line in enumerate(f)}, status=status.HTTP_200_OK)
            except OSError:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        logs = sorted([l for l in os.listdir(log_dir) if l.startswith("temperature-") and l.endswith(".log")])
        data = {n: l for n, l in enumerate(logs)}
        return Response(data, status=status.HTTP_200_OK)
