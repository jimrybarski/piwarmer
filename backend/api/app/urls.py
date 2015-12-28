from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rpidapi import views

router = DefaultRouter(trailing_slash=False)

router.register(r'user', views.ScientistViewset, base_name='scientist')
# temperature control programs created by users
router.register(r'program', views.ProgramViewset, base_name='program')
# PID values for heating devices
router.register(r'driver', views.DriverViewset, base_name='driver')

# Deactivate the heater and stop the current program
stop = url(r'stop', views.StopView.as_view())
# Start a temperature control program
start = url(r'start', views.StartView.as_view())
# Find out the current state of things (e.g. temperature, duty cycle, etc)
current = url(r'current', views.CurrentView.as_view())
# See a list of previous runs and their temperatures over time
temperature_logs = url(r'logs', views.TemperatureLogView.as_view())


urlpatterns = [url(r'^backend/', include(router.urls)), stop, start, current, temperature_logs]
