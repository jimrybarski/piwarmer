from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rpidapi import views

router = DefaultRouter(trailing_slash=False)

router.register(r'user', views.ScientistViewset, base_name='scientist')
router.register(r'program', views.ProgramViewset, base_name='program')
router.register(r'driver', views.DriverViewset, base_name='driver')

stop = url(r'stop', views.StopView.as_view())
start = url(r'start', views.StartView.as_view())
current = url(r'current', views.CurrentView.as_view())

urlpatterns = [url(r'^backend/', include(router.urls)), stop, start, current]