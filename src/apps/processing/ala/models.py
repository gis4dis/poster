import uuid
from django.db import models

class Property(models.Model):
    name_id = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=30)
    unit = models.CharField(max_length=30)

class SamplingFeature(models.Model):
    provider_id = models.CharField(max_length=50)
    name = models.CharField(max_length=50)

class Observation(models.Model):
    phenomenon_time = models.DateTimeField()
    observed_property = models.ForeignKey(Property, related_name='observations')
    feature_of_interest = models.ForeignKey(SamplingFeature, related_name='observations')
    result = models.DecimalField(max_digits=8, decimal_places=3)
    # provider_log = models.ForeignKey('importing.ProviderLog', to_field='uuid4', related_name='observations')

    class Meta:
        unique_together=(('phenomenon_time','observed_property','feature_of_interest'),)
