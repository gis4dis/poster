# urls.py
from django.conf.urls import url
from .views import MCAppTemplateView

app_name = 'mc'

urlpatterns = [
    url(
        r'^$',
        MCAppTemplateView.as_view(),
        name="mc-app"
        ),
]
