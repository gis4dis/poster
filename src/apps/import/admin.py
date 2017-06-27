from django.contrib import admin

from .models import Provider, ProviderLog


class ProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']

    fields = ['name', 'code']
    readonly_fields = ['token', 'url']

    add_fields = fields
    change_fields = fields + readonly_fields

    def add_view(self, request, form_url='', extra_context=None):
        self.fields = self.add_fields
        return super(ProviderAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.fields = self.change_fields
        return super(ProviderAdmin, self).change_view(request, object_id, form_url, extra_context)


class ProviderLogAdmin(admin.ModelAdmin):
    list_display = ['provider', 'content_type', 'received_time', 'is_valid', ]
    list_filter = ['provider__name', 'content_type', 'received_time', 'is_valid', ]


admin.site.register(Provider, ProviderAdmin)
admin.site.register(ProviderLog, ProviderLogAdmin)
