import logging
from django.core.management.base import BaseCommand
from apps.processing.ala.util import util
from dateutil.parser import parse
from dateutil import relativedelta
from datetime import date, timedelta
from apps.common.models import Process, Property
from apps.processing.ala.models import SamplingFeature, Observation
import luminol

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import data from ALA stations. Optionally you can pass date, ' \
           'otherwise it will fetch the day before yesterday data.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        process = Process.objects.get(name_id='avg_hour')

        print("hello", process, obss)

