from .models import Property, SamplingFeature, Observation
from django.contrib import admin


class PropertyAdmin(admin.ModelAdmin):
    pass

class SamplingFeatureAdmin(admin.ModelAdmin):
    pass

class ObservationAdmin(admin.ModelAdmin):
    pass





admin.site.register(Property, PropertyAdmin)
admin.site.register(SamplingFeature, SamplingFeatureAdmin)
admin.site.register(Observation, ObservationAdmin)
