import logging
from django.core.management.base import BaseCommand
from apps.processing.ala.util import util
from dateutil.parser import parse
from dateutil import relativedelta
from datetime import date, timedelta
from apps.common.models import Process, Property
from apps.processing.ala.models import SamplingFeature, Observation
import luminol
from psycopg2.extras import DateTimeTZRange

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    # help = 'Import data from ALA stations. Optionally you can pass date, ' \
    #        'otherwise it will fetch the day before yesterday data.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        station = SamplingFeature.objects.get(id_by_provider='11359205')

        prop = Property.objects.get(name_id='air_temperature')

        process = Process.objects.get(name_id='measure')

        obss = Observation.objects.filter(
            feature_of_interest=station
            , observed_property=prop
            , procedure=process
        )
        process2 = Process.objects.get(name_id='anomaly')

        for obj in obss:
            result = 233
            result_null_reason = ''
            obs = Observation.objects.create(
                phenomenon_time_range=obj.phenomenon_time_range,
                observed_property=obj.observed_property,
                feature_of_interest=obj.feature_of_interest,
                procedure=process2,
                result=result,
                result_null_reason=result_null_reason,
            )
            obs.related_observations.set(obss)

        print("finish")