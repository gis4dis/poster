# from django.db import models
from django.utils.timezone import localtime
from django.contrib.gis.db import models

from django.contrib.postgres import fields as pgmodels


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


class AbstractFeature(models.Model):
    """Place where the observation were collected - mostly point feature like weather station."""

    id_by_provider = models.CharField(
        help_text="ID of the station used by provider.",
        max_length=50,
        editable=False
    )

    name = models.CharField(
        help_text="Human-readable name of the station.",
        max_length=50
    )

    # https://docs.djangoproject.com/en/1.10/topics/db/models/#field-name-hiding-is-not-permitted
    # This field is supposed to be overridden in subclass if needed.
    # By default it is set to point geometry (PointField) but could be either changed on other type (LineField)
    #   or completely removed (set to None)
    # https://docs.djangoproject.com/en/1.11/ref/contrib/gis/model-api/#pointfield
    #
    # Spatial fields defaults to srid=4326 (WGS84)
    geometry = models.PointField(
        help_text="Spatial information about feature."
    )

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


class AbstractObservation(models.Model):
    """An observation is an act associated with a discrete time instant or
    period through which a quantity is assigned to a phenomenon (Property).
    It involves application of a specified procedure (Process), such as a
    sensor measurement or algorithm processing (e.g. hourly average)."""

    phenomenon_time_range = pgmodels.DateTimeRangeField(
        help_text="Datetime range when the observation was captured.",
    )

    # phenomenon_time = models.DateTimeField(
    #     help_text="Beginning of the observation.",
    #     editable=False
    # )
    #
    # phenomenon_time_to = models.DateTimeField(
    #     help_text="End of the observation. If the observation was instant, "
    #               "it is the same time as phenomenon_time.",
    #     editable=False
    # )

    observed_property = models.ForeignKey(
        Property,
        help_text="Phenomenon that was observed, e.g. air temperature.",
        related_name='observations',
        editable=False
    )

    # NOTE: This field has to be overridden in child classes!
    #       It needs to reference proper ForeignKey (Concrete Feature inherited from AbstractFeature)
    feature_of_interest = models.ForeignKey(
        AbstractFeature,
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

    class Meta:
        abstract = True
        get_latest_by = 'phenomenon_time_range'
        ordering = ['-phenomenon_time_range', 'feature_of_interest', 'procedure',
                    'observed_property']
        unique_together = (('phenomenon_time_range',
                            'observed_property', 'feature_of_interest',
                            'procedure'),)

    @property
    def _phenomenon_time_is_period(self):
        """Returns true if phenomenon time is interval."""
        # return self.phenomenon_time != self.phenomenon_time_to
        return self.phenomenon_time_range.upper is not None

    def __str__(self):
        return "{} of {} at station {} {}".format(
            self.procedure.name,
            self.observed_property.name,
            self.feature_of_interest.name,
            localtime(self.phenomenon_time).strftime('%Y-%m-%d %H:%M UTC%z')
        )
