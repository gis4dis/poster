from .models import Property, SamplingFeature, Observation, Process
from django.contrib import admin


class PropertyAdmin(admin.ModelAdmin):
    readonly_fields=(
        'name_id',
    )

class ProcessAdmin(admin.ModelAdmin):
    readonly_fields=(
        'name_id',
    )

class SamplingFeatureAdmin(admin.ModelAdmin):
    readonly_fields=(
        'id_by_provider',
    )

class ObservationAdmin(admin.ModelAdmin):
    readonly_fields=(
        'phenomenon_time',
        'phenomenon_time_to',
        'observed_property',
        'feature_of_interest',
        'procedure',
        'related_observations',
        'result',
    )


admin.site.register(Property, PropertyAdmin)
admin.site.register(Process, ProcessAdmin)
admin.site.register(SamplingFeature, SamplingFeatureAdmin)
admin.site.register(Observation, ObservationAdmin)
