import logging
from django.core.management.base import BaseCommand
from apps.processing.ala.util import util
from dateutil.parser import parse
from datetime import date, timedelta

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import data from ALA stations, optionally you can pass date. Otherwise it will fetch yesterday data'

    def add_arguments(self, parser):
        parser.add_argument('date', nargs='?', type=parse, default=None)

    def handle(self, *args, **options):

        stations = util.get_or_create_stations()
        day = options['date']
        if day is None:
            day = date.today() - timedelta(1)

        logger.info(
            'Importing observations of {} ALA stations from {}.'.format(
                len(stations),
                day
            )
        )

        try:
            for station in stations:
                util.load(station, day)
                util.create_avgs(station, day)
        except Exception as e:
            self.stdout.write(self.style.ERROR(e))
