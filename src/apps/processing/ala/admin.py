from .models import SamplingFeature, Observation
from django.contrib import admin


class SamplingFeatureAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id_by_provider',
    )


class ObservationAdmin(admin.ModelAdmin):
    list_display = (
        'phenomenon_time',
        'phenomenon_time_to',
        'observed_property',
        'feature_of_interest',
        'procedure',
        'result',
    )
    list_filter = (
        'phenomenon_time',
        ('observed_property', admin.RelatedOnlyFieldListFilter),
        ('feature_of_interest', admin.RelatedOnlyFieldListFilter),
        ('procedure', admin.RelatedOnlyFieldListFilter),
    )
    readonly_fields = (
        'phenomenon_time',
        'phenomenon_time_to',
        'observed_property',
        'feature_of_interest',
        'procedure',
        'related_observations',
        'result',
        'result_null_reason',
    )


admin.site.register(SamplingFeature, SamplingFeatureAdmin)
admin.site.register(Observation, ObservationAdmin)
