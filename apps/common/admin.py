from .models import Property, Process
from django.contrib import admin


class PropertyAdmin(admin.ModelAdmin):
    readonly_fields = (
        'name_id',
    )


class ProcessAdmin(admin.ModelAdmin):
    readonly_fields = (
        'name_id',
    )


admin.site.register(Property, PropertyAdmin)
admin.site.register(Process, ProcessAdmin)
