# urls.py
from django.urls import path
from apps.common.admin_additions.views import SettingsView, StaticfilesView

app_name = 'common_admin'

urlpatterns = [
    path('', SettingsView.as_view()),
    path('staticfiles/', StaticfilesView.as_view()),
]