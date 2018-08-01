# urls.py
from django.conf.urls import url
from django.views.generic import TemplateView

from .views import MCAppTemplateView

app_name = 'mc'

urlpatterns = [
    url(
        r'^$',
        TemplateView.as_view(template_name="mc/index.html"),
        name="mc-app"
        ),
]
