import uuid
from django.db import models
from django.template import defaultfilters
from datetime import timedelta, timezone
from django.utils.timezone import localtime


class Property(models.Model):
    """Physical phenomenon related to weather, e.g. air temperature."""
    name_id = models.CharField(
        help_text="Unique and computer-friendly name of the property.",
        max_length=30,
        unique=True,
        editable=False
    )
    name = models.CharField(
        help_text="Human-readable name of the property.",
        max_length=30
    )
    unit = models.CharField(
        help_text="Unit of observations (physical unit). Same for all "
                  "observations of the property.",
        max_length=30
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = "properties"

    def __str__(self):
        return self.name


class SamplingFeature(models.Model):
    """Weather station."""
    id_by_provider = models.CharField(
        help_text="ID of the station used by provider (ALA).",
        max_length=50,
        editable=False
    )
    name = models.CharField(
        help_text="Human-readable name of the station.",
        max_length=50
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Process(models.Model):
    """Process used to generate the result, e.g. measurement or
    hourly average."""
    name_id = models.CharField(
        help_text="Unique and computer-friendly name of the process.",
        max_length=30,
        unique=True,
        editable=False
    )
    name = models.CharField(
        help_text="Human-readable name of the process.",
        max_length=50
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = "processes"

    def __str__(self):
        return self.name


class Observation(models.Model):
    """An observation is an act associated with a discrete time instant or
    period through which a quantity is assigned to a phenomenon (Property).
    It involves application of a specified procedure (Process), such as a
    sensor measurement or algorithm processing (e.g. hourly average)."""
    phenomenon_time = models.DateTimeField(
        help_text="Beginning of the observation.",
        editable=False
    )
    phenomenon_time_to = models.DateTimeField(
        help_text="End of the observation. If the observation was instant, "
                  "it is the same time as phenomenon_time.",
        editable=False
    )
    observed_property = models.ForeignKey(
        Property,
        help_text="Phenomenon that was observed, e.g. air temperature.",
        related_name='observations',
        editable=False
    )
    feature_of_interest = models.ForeignKey(
        SamplingFeature,
        help_text="Weather station where the observation was taken.",
        related_name='observations',
        editable=False
    )
    procedure = models.ForeignKey(
        Process,
        help_text="Process used to generate the result, e.g. measurement or "
                  "average.",
        related_name='observations',
        editable=False
    )
    related_observations = models.ManyToManyField(
        'self',
        help_text="Measured observations that were used to generate average "
                  "observation, or vice versa.",
        editable=False
    )
    result = models.DecimalField(
        help_text="Numerical value of the measured phenomenon in units "
                  "specified by Process.",
        max_digits=8,
        decimal_places=3,
        editable=False
    )

    # provider_log = models.ForeignKey('importing.ProviderLog',
    # to_field='uuid4', related_name='observations')

    class Meta:
        get_latest_by = 'phenomenon_time'
        ordering = ['-phenomenon_time', 'feature_of_interest', 'procedure',
                    'observed_property']
        unique_together = (('phenomenon_time', 'phenomenon_time_to',
                            'observed_property', 'feature_of_interest',
                            'procedure'),)

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
