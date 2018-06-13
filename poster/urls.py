from django.contrib import admin
from django.urls import path, include

from django.conf.urls import url
from rest_framework import routers
from apps.mc import views

router = routers.DefaultRouter()
router.register(r'properties', views.PropertyViewSet)
router.register(r'timeseries', views.TimeSeriesViewSet, base_name='timeseries')

urlpatterns = [
    url(r'^api/v1/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('import/', include('apps.importing.urls')),
]
