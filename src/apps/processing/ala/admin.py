from .models import SamplingFeature, Observation
from django.contrib import admin


class SamplingFeatureAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id_by_provider',
    )


class ObservationAdmin(admin.ModelAdmin):
    readonly_fields = (
        'phenomenon_time',
        'phenomenon_time_to',
        'observed_property',
        'feature_of_interest',
        'procedure',
        'related_observations',
        'result',
    )


admin.site.register(SamplingFeature, SamplingFeatureAdmin)
admin.site.register(Observation, ObservationAdmin)
