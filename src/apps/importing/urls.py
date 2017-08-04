# urls.py
from django.conf.urls import url
from .views import ImportView

app_name = 'importing'

urlpatterns = [
    url(
        r'^(?P<code>[\w-]+)/(?P<token>[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12})/(?P<file_name>[\w-]{1,32})(?:\.(?P<ext>[0-9a-z]{1,16}))?$',
        ImportView.as_view(),
        name="provider"
        ),
]
