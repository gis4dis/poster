from django.db import models
from apps.common.models import AbstractFeature, AbstractObservation


class SamplingFeature(AbstractFeature):
    # Ala doesn't have geometry value to the yet - to be added in future
    geometry = None


class Observation(AbstractObservation):
    # TODO: migrate this to general Observation model
    phenomenon_time_range = None

    phenomenon_time = models.DateTimeField(
        help_text="Beginning of the observation.",
        editable=False
    )

    phenomenon_time_to = models.DateTimeField(
        help_text="End of the observation. If the observation was instant, "
                  "it is the same time as phenomenon_time.",
        editable=False
    )

    # NOTE: see parent class for more information
    feature_of_interest = models.ForeignKey(
        SamplingFeature,
        help_text="Weather station where the observation was taken.",
        related_name='observations',
        editable=False
    )

    class Meta:
        get_latest_by = 'phenomenon_time'
        ordering = ['-phenomenon_time', 'feature_of_interest', 'procedure',
                    'observed_property']
        unique_together = (('phenomenon_time', 'phenomenon_time_to',
                            'observed_property', 'feature_of_interest',
                            'procedure'),)

    @property
    def _phenomenon_time_is_period(self):
        """Returns true if phenomenon time is interval."""
        return self.phenomenon_time != self.phenomenon_time_to
        # return self.phenomenon_time_range.upper is not None
