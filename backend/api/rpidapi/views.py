from interface import CurrentState
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
import serializers
import logging
import models
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
        # We implement get_queryset so that a user will only see their own programs.
        # Not a security thing, just a convenience.
        if 'user' in self.request.query_params.keys():
            return models.Program.objects.filter(scientist=self.request.query_params['user'])
        return models.Program.objects.all()


class StartView(APIView):
    """
    The endpoint that will start a program.

    """
    def post(self, request, format=None):
        current_state = CurrentState()
        try:
            log.info("Program start requested")
            # look up the driver and program in the database
            driver = models.Driver.objects.get(id=request.data['driver'])
            program = models.Program.objects.get(id=request.data['program'])
            # convert to JSON, which our Python backend is expecting
            json_driver = serializers.DriverSerializer(driver)
            json_program = serializers.ProgramSerializer(program)
            # update the selected driver and program in Redis, so that our backend can know which ones to use
            current_state.driver = json_driver.data
            current_state.program = json_program.data['steps']
        except Exception as e:
            log.exception("Could not start program")
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": e.message})
        else:
            # Flip the switch and the backend will start running the program once it detects the change (usually within a second)
            current_state.activate()
        log.info("Program started fine")
        return Response(status=status.HTTP_200_OK)


class StopView(APIView):
    """
    The endpoint that will reset everything and shut off the heater.

    """
    def post(self, request, format=None):
        log.info("Stop program requested")
        current_state = CurrentState()
        # Turn off the heater
        current_state.deactivate()
        # Delete the program and driver from Redis so that the backend realizes we're done
        current_state.clear()
        log.info("Program stopped OK")
        return Response(status=status.HTTP_200_OK)


class CurrentView(APIView):
    """
    The endpoint that provides the current temperature and the action that the controller is performing.

    """
    def get(self, request, format=None):
        current_state = CurrentState()
        out = {"step": current_state.current_step,
               "temp": current_state.current_temp,
               }
        return Response(out, status=status.HTTP_200_OK)


class TemperatureLogView(APIView):
    """
    SHOULD provide links to each log, so you can see their data, however it currently just shows a list of logs available.

    """
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
