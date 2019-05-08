from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import TemplateView


# noinspection PyUnresolvedReferences
class SuperAdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class SettingsView(LoginRequiredMixin, SuperAdminRequiredMixin, TemplateView):
    login_url = '/admin/login/'
    template_name = "admin/common/settings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        settings_dict = {}
        for name in settings.__dict__:
            settings_dict[name] = getattr(settings, name)
        context['settings'] = settings_dict
        return context


class StaticfilesView(LoginRequiredMixin, SuperAdminRequiredMixin, TemplateView):
    template_name = 'admin/common/staticfiles.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        import os
        from django.conf import settings
        read_data = ""
        read_dir = os.listdir(settings.STATIC_ROOT)
        with open(settings.STATIC_ROOT + '/staticfiles.json', 'r') as f:
            read_data = f.read()
        context['staticfiles'] = read_data
        return context
