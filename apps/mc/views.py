from django.views.generic import TemplateView


class MCAppTemplateView(TemplateView):
    template_name = "apps/mc/map/index.html"
