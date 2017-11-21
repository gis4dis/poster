import uuid
from django.db import models
from django.utils.timezone import localtime


class Property(models.Model):
    """Attribute of an object referenced by a name."""
    name_id = models.CharField(
        help_text="Unique and computer-friendly name of the property.",
        max_length=30,
        unique=True,
        editable=False
    )
    name = models.CharField(
        help_text="Human-readable name of the property.",
        max_length=100
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


class Zsj(models.Model):
    """Basic residential unit in the Czech rep., officially called 'Zakladni
    sidelni jednotka'."""
    id_by_provider = models.CharField(
        help_text="ID of the ZSJ used by Czech law.",
        max_length=100,
        editable=False
    )
    name = models.CharField(
        help_text="Human-readable name of the ZSJ.",
        max_length=100
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name + ', ' + self.id_by_provider


class MobilityStream(models.Model):
    """Mobility stream from one ZSJ to another."""
    src_zsj = models.ForeignKey(
        Zsj,
        help_text="Source ZSJ, where people are departing.",
        related_name='arrival_streams',
        editable=False
    )
    dst_zsj = models.ForeignKey(
        Zsj,
        help_text="Destination ZSJ, where people are arriving.",
        related_name='to_streams',
        editable=False
    )
    opposite = models.OneToOneField(
        'self',
        help_text="Stream in opposite direction to this stream.",
        editable=False,
        null=True,
    )

    class Meta:
        ordering = ['src_zsj__name', 'dst_zsj__name']
        unique_together = (
            (
                'src_zsj',
                'dst_zsj',
            ),
        )

    def __str__(self):
        return self.src_zsj.name + '->' + self.dst_zsj.name


class Process(models.Model):
    """Process used to generate the result, e.g. estimation."""
    name_id = models.CharField(
        help_text="Unique and computer-friendly name of the process.",
        max_length=30,
        unique=True,
        editable=False
    )
    name = models.CharField(
        help_text="Human-readable name of the process.",
        max_length=100
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = "processes"

    def __str__(self):
        return self.name


ANY_OCCURRENCE = "0"
TRANSIT_OCCURRENCE = "1"
VISIT_OCCURRENCE = "2"
OCCURRENCE_CHOICES = (
    (ANY_OCCURRENCE, 'Any'),
    (TRANSIT_OCCURRENCE, 'Transit'),
    (VISIT_OCCURRENCE, 'Visit'),
)
UNIQUES_ALL = "0"
UNIQUES_UNIQUE = "1"
UNIQUES_CHOICES = (
    (UNIQUES_ALL, 'All'),
    (UNIQUES_UNIQUE, 'Uniques'),
)


class MobilityObservation(models.Model):
    phenomenon_time = models.DateTimeField(
        help_text="Beginning of the observation.",
        editable=False
    )
    phenomenon_time_to = models.DateTimeField(
        help_text="End of the observation.",
        editable=False
    )
    observed_property = models.ForeignKey(
        Property,
        help_text="Phenomenon that was observed, e.g. mobility.",
        related_name='observations',
        editable=False
    )
    feature_of_interest = models.ForeignKey(
        MobilityStream,
        help_text="Stream station where the observation was taken.",
        related_name='observations',
        editable=False
    )
    procedure = models.ForeignKey(
        Process,
        help_text="Process used to generate the result, e.g. estimation.",
        related_name='observations',
        editable=False
    )
    src_occurrence_type = models.CharField(
        help_text="Occurrence type in the source ZSJ.",
        max_length=1,
        choices=OCCURRENCE_CHOICES,
        default=ANY_OCCURRENCE,
    )
    dst_occurrence_type = models.CharField(
        help_text="Occurrence type in the destination ZSJ.",
        max_length=1,
        choices=OCCURRENCE_CHOICES,
        default=ANY_OCCURRENCE,
    )
    uniques_type = models.CharField(
        help_text="All or only uniques.",
        max_length=1,
        choices=UNIQUES_CHOICES,
        default=UNIQUES_ALL,
    )
    result = models.PositiveIntegerField(
        help_text="Numerical value of the measured phenomenon in units "
                  "specified by Process.",
        null=True,
        editable=False,
    )
    result_null_reason = models.CharField(
        help_text="Reason why result is null.",
        max_length=100,
    )

    class Meta:
        get_latest_by = 'phenomenon_time'
        ordering = [
            '-phenomenon_time',
            'feature_of_interest',
            'procedure',
            'observed_property'
        ]
        unique_together = (
            (
                'phenomenon_time',
                'phenomenon_time_to',
                'observed_property',
                'feature_of_interest',
                'procedure',
                'src_occurrence_type',
                'dst_occurrence_type',
                'uniques_type',
            ),
        )

    def _phenomenon_time_is_period(self):
        "Returns true if phenomenon time is interval."
        return self.phenomenon_time != self.phenomenon_time_to

    phenomenon_time_is_period = property(_phenomenon_time_is_period)

    def __str__(self):
        if self.result is not None:
            res_str = "{}".format(self.result)
        else:
            res_str = 'unknown because of {}'.format(self.result_null_reason)

        return "{} from {} to {} on {} ({} -> {}, {}) was {}".format(
            self.observed_property.name,
            self.feature_of_interest.src_zsj.name,
            self.feature_of_interest.dst_zsj.name,
            localtime(self.phenomenon_time).strftime('%Y-%m-%d'),
            self.get_src_occurrence_type_display(),
            self.get_dst_occurrence_type_display(),
            self.get_uniques_type_display(),
            res_str
        )
