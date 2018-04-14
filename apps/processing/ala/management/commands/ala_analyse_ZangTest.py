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
        stations = util.get_or_create_stations()
        # station = stations[0]
        station = SamplingFeature.objects.get(id_by_provider='11359205')

        props = util.get_or_create_props()
        # prop = props[1]
        prop = Property.objects.get(name_id='air_temperature')

        processes = util.get_or_create_processes()
        measure_process = processes[0]

        obss = Observation.objects.filter(
            feature_of_interest=station
            , observed_property=prop
            , procedure=measure_process
        )

        for obj in obss:
            print(obj.feature_of_interest, obj.result)
            print(obj.phenomenon_time_range.lower,'\r\n')

        print(station)
        print(prop)
        print(measure_process)
