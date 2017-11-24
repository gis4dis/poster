from django.db import models
from apps.common.models import AbstractFeature, AbstractObservation


class SamplingFeature(AbstractFeature):
    # Ala doesn't have geometry value to the yet - to be added in future
    geometry = None


class Observation(AbstractObservation):

    # NOTE: see parent class for more information
    feature_of_interest = models.ForeignKey(
        SamplingFeature,
        help_text="Weather station where the observation was taken.",
        related_name='observations',
        editable=False
    )


class Property(models.Model):
    """Physical phenomenon related to weather, e.g. air temperature."""

    name_id = models.CharField(
        help_text="Unique and computer-friendly name of the property. eg. ('precipitation' or 'air_temperature')",
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


class Process(models.Model):
    """Process used to generate the result, e.g. measurement or
    hourly average."""
    name_id = models.CharField(
        help_text="Unique and computer-friendly name of the process. eg. ('measure' or 'avg_hour')",
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