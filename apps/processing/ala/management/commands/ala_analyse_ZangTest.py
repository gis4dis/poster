import logging
from django.core.management.base import BaseCommand
from apps.common.models import Process, Property
from apps.processing.ala.models import SamplingFeature, Observation

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    # help = 'Import data from ALA stations. Optionally you can pass date, ' \
    #        'otherwise it will fetch the day before yesterday data.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        station = SamplingFeature.objects.get(id_by_provider='11359205')

        prop = Property.objects.get(name_id='precipitation')

        process = Process.objects.get(name_id='measure')

        raw_obss = Observation.objects.filter(
            feature_of_interest=station
            , observed_property=prop
            , procedure=process
        )

        score = []

        for i in range(0, len(raw_obss)):
            score.append(i)

        # mainpart
        anomaly_score_save(raw_obss, score)


def anomaly_score_save(raw_obss, score):

    anomaly_process = Process.objects.get(name_id='anomaly')

    for i in range(0, len(raw_obss)):
        new_obs = Observation.objects.create(
            phenomenon_time_range=raw_obss[i].phenomenon_time_range,
            observed_property=raw_obss[i].observed_property,
            feature_of_interest=raw_obss[i].feature_of_interest,
            procedure=anomaly_process,
            result=score[i],
            result_null_reason='',
        )
        new_obs.related_observations.set(raw_obss)
    print("Saved successfully")
