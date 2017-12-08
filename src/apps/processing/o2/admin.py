from .models import Zsj, MobilityStream, Property, Process, \
    MobilityObservation, SocioDemoObservation
from django.contrib import admin


class PropertyAdmin(admin.ModelAdmin):
    readonly_fields = (
        'name_id',
    )


class ProcessAdmin(admin.ModelAdmin):
    readonly_fields = (
        'name_id',
    )


class MobilityStreamAdmin(admin.ModelAdmin):
    readonly_fields = (
        'src_zsj',
        'dst_zsj',
    )


class ZsjAdmin(admin.ModelAdmin):
    readonly_fields = (
        'id_by_provider',
    )


class MobilityObservationAdmin(admin.ModelAdmin):
    readonly_fields = (
        'phenomenon_time',
        'phenomenon_time_to',
        'observed_property',
        'feature_of_interest',
        'procedure',
        'src_occurrence_type',
        'dst_occurrence_type',
        'uniques_type',
        'result',
        'result_null_reason',
    )


class SocioDemoObservationAdmin(admin.ModelAdmin):
    readonly_fields = (
        'phenomenon_time_range',
        'observed_property',
        'feature_of_interest',
        'procedure',
        'age',
        'gender',
        'occurrence_type',
        'result_for_human',
    )


admin.site.register(Property, PropertyAdmin)
admin.site.register(Process, ProcessAdmin)
admin.site.register(Zsj, ZsjAdmin)
admin.site.register(MobilityStream, MobilityStreamAdmin)
admin.site.register(MobilityObservation, MobilityObservationAdmin)
admin.site.register(SocioDemoObservation, SocioDemoObservationAdmin)
