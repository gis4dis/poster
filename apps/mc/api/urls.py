from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from .views import PropertyViewSet, TimeSeriesViewSet

app_name = 'api-mc'


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'properties', PropertyViewSet)
router.register(r'timeseries', TimeSeriesViewSet, base_name='timeseries')


urlpatterns = [
    url(r'^', include(router.urls)),
]
