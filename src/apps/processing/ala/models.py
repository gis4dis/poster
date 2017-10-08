import uuid
from django.db import models
from django.template import defaultfilters
from datetime import timedelta, timezone
from django.utils.timezone import localtime

class Property(models.Model):
    name_id = models.CharField(max_length=30, unique=True, editable=False)
    name = models.CharField(max_length=30)
    unit = models.CharField(max_length=30)

    class Meta:
        ordering=['name']
        verbose_name_plural = "properties"

    def __str__(self):
        return self.name

class SamplingFeature(models.Model):
    id_by_provider = models.CharField(max_length=50, editable=False)
    name = models.CharField(max_length=50)

    class Meta:
        ordering=['name']

    def __str__(self):
        return self.name

class Process(models.Model):
    name_id = models.CharField(max_length=30, unique=True, editable=False)
    name = models.CharField(max_length=50)

    class Meta:
        ordering=['name']
        verbose_name_plural = "processes"

    def __str__(self):
        return self.name

class Observation(models.Model):
    phenomenon_time = models.DateTimeField(
        help_text="Time that the result applies to the property of the feature-of-interest. This is often the time of interaction by a sampling procedure or observation procedure with a real-world feature.",
        editable=False
    )
    phenomenon_time_to = models.DateTimeField(editable=False)
    observed_property = models.ForeignKey(Property, related_name='observations', editable=False)
    feature_of_interest = models.ForeignKey(SamplingFeature, related_name='observations', editable=False)
    procedure = models.ForeignKey(Process, related_name='observations', editable=False)
    related_observations = models.ManyToManyField('self', editable=False)
    result = models.DecimalField(max_digits=8, decimal_places=3, editable=False)
    # provider_log = models.ForeignKey('importing.ProviderLog', to_field='uuid4', related_name='observations')

    class Meta:
        get_latest_by='phenomenon_time'
        ordering=['-phenomenon_time', 'feature_of_interest', 'procedure', 'observed_property']
        unique_together=(('phenomenon_time','phenomenon_time_to','observed_property','feature_of_interest','procedure'),)

    def _phenomenon_time_is_period(self):
        "Returns true if phenomenon time is interval."
        return self.phenomenon_time != self.phenomenon_time_to
    phenomenon_time_is_period = property(_phenomenon_time_is_period)

    def __str__(self):
        return "{} of {} at station {} {}".format(
            self.procedure.name,
            self.observed_property.name,
            self.feature_of_interest.name,
            localtime(self.phenomenon_time).strftime('%Y-%m-%d %H:%M UTC%z')
        )
