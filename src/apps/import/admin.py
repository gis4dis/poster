from django.contrib import admin

from .models import Provider, ProviderLog, ReadonlyProviderLog


class FieldsMixin:

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

    fields = ['provider', 'content_type', 'body', ('file_name', 'ext'), 'file_path', 'received_time', 'is_valid', ]


class ReadonlyProviderLogAdmin(FieldsMixin, admin.ModelAdmin):
    list_display = ['provider', 'content_type', 'received_time', 'is_valid', ]
    list_filter = ['provider__name', 'content_type', 'received_time', 'is_valid', ]

    default_fields = ['provider', 'content_type', 'body', 'file_name', 'file_path', 'ext', 'received_time', 'is_valid', ]
    default_readonly_fields = []

    add_fields = ['provider', 'content_type', 'body', 'file_name', 'ext', 'received_time', 'is_valid', ]
    change_fields = ['provider', 'content_type', 'body', ('file_name', 'ext'), 'file_path', 'received_time', 'is_valid', ]
    change_readonly_fields = ['provider', 'content_type', 'body', 'file_name', 'ext', 'file_path', 'received_time', 'is_valid', ]


admin.site.register(Provider, ProviderAdmin)
admin.site.register(ProviderLog, ProviderLogAdmin)
admin.site.register(ReadonlyProviderLog, ReadonlyProviderLogAdmin)
