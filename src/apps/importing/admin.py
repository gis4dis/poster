from functools import update_wrapper

from django.contrib import admin
from django.db.models import Count, DateTimeField, Min, Max
from django.db.models.functions import Trunc

from .models import Provider, ProviderLog, ReadonlyProviderLog


class FieldsMixin(object):

    def add_view(self, request, form_url='', extra_context=None):
        try:
            if hasattr(self, 'add_fields'):
                self.fields = self.add_fields
            elif hasattr(self, 'default_fields'):
                self.fields = self.default_fields
            elif hasattr(self, 'fields'):
                del self.fields
        except:
            pass

        try:
            if hasattr(self, 'add_readonly_fields'):
                self.readonly_fields = self.add_readonly_fields
            elif hasattr(self, 'default_readonly_fields'):
                self.readonly_fields = self.default_readonly_fields
            elif hasattr(self, 'readonly_fields'):
                del self.readonly_fields
        except:
            pass
        return super(FieldsMixin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        try:
            if hasattr(self, 'change_fields'):
                self.fields = self.change_fields
            elif hasattr(self, 'default_fields'):
                self.fields = self.default_fields
            elif hasattr(self, 'fields'):
                del self.fields
        except:
            pass

        try:
            if hasattr(self, 'change_readonly_fields'):
                self.readonly_fields = self.change_readonly_fields
            elif hasattr(self, 'default_readonly_fields'):
                self.readonly_fields = self.default_readonly_fields
            elif hasattr(self, 'readonly_fields'):
                del self.readonly_fields
        except:
            pass

        return super(FieldsMixin, self).change_view(request, object_id, form_url, extra_context)


class ProviderAdmin(FieldsMixin, admin.ModelAdmin):
    list_display = ['name', 'code']

    fields = ['name', 'code']
    readonly_fields = ['token', 'url']

    add_fields = fields
    change_fields = fields + readonly_fields


class ProviderLogAdmin(FieldsMixin, admin.ModelAdmin):
    list_display = ['provider', 'content_type', 'received_time', 'is_valid', ]
    list_filter = ['provider__name', 'content_type', 'received_time', 'is_valid', ]

    fields = ['provider', 'content_type', 'body', ('file_name', 'ext'), 'file_path', 'received_time', 'is_valid',  'uuid4',]
    readonly_fields = ['uuid4',]


# https://medium.com/@hakibenita/how-to-turn-django-admin-into-a-lightweight-dashboard-a0e0bbf609ad
# Wonderful way to add some graphs :)
class ReadonlyProviderLogAdmin(FieldsMixin, admin.ModelAdmin):
    change_list_template = 'admin/readonly_provider_change_list.html'
    date_hierarchy = 'received_time'

    list_display = ['provider', 'content_type', 'received_time', 'is_valid', ]
    list_filter = ['received_time', 'provider__name', 'content_type', 'is_valid', ]

    default_fields = ['provider', 'content_type', 'file_name', 'file_path', 'ext', 'received_time', 'is_valid', 'uuid4', 'parsed_body']
    default_readonly_fields = []

    add_fields = ['provider', 'content_type', 'body', 'file_name', 'ext', 'received_time', 'is_valid', ]
    change_fields = ['provider', 'content_type', ('file_name', 'ext'), 'file_path', 'received_time', 'is_valid', 'uuid4', 'parsed_body']
    change_readonly_fields = ['provider', 'content_type', 'file_name', 'ext', 'file_path', 'received_time', 'is_valid', 'uuid4', 'parsed_body']

    def stats_view(self, request, extra_context=None):

        def get_next_in_date_hierarchy(request, date_hierarchy):
            if date_hierarchy + '__day' in request.GET:
                return 'hour'
            if date_hierarchy + '__month' in request.GET:
                return 'day'
            if date_hierarchy + '__year' in request.GET:
                return 'month'
            return 'month'

        response = self.changelist_view(request, extra_context)
        response.template_name = 'admin/readonly_provider_log_summary_change_list.html'

        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total': Count('id'),
        }

        summary = list(
            qs.values('provider__name')
              .annotate(**metrics)
              .order_by('-total')
        )
        response.context_data['summary'] = summary

        summary_total = dict(
            qs.aggregate(**metrics)
        )
        response.context_data['summary_total'] = summary_total

        period = get_next_in_date_hierarchy(
            request,
            self.date_hierarchy,
        )
        response.context_data['period'] = period

        summary_over_time = qs.annotate(
            period=Trunc(
                'received_time',
                period,
                output_field=DateTimeField(),
            ),
        )\
            .values('period')\
            .annotate(total=Count('id'))\
            .order_by('period')

        summary_range = summary_over_time.aggregate(
            low=Min('total'),
            high=Max('total'),
        )

        high = summary_range.get('high', 0)
        low = summary_range.get('low', 0)

        response.context_data['summary_over_time'] = [
            {
                'period': x['period'],
                'total': x['total'] or 0,
                'pct':
                    ((x['total'] or 0) / high) * 100
                    if high > low else 100,
            } for x in summary_over_time]

        return response

    def get_urls(self):
        urlpatterns = super(ReadonlyProviderLogAdmin, self).get_urls()

        from django.conf.urls import url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = [
            url(r'^statistics/$', wrap(self.stats_view), name='%s_%s_statistics' % info),
        ] + urlpatterns
        return urlpatterns


admin.site.register(Provider, ProviderAdmin)
admin.site.register(ProviderLog, ProviderLogAdmin)
admin.site.register(ReadonlyProviderLog, ReadonlyProviderLogAdmin)
