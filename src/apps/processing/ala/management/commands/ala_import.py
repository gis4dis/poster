from django.core.management.base import BaseCommand, CommandError
from apps.processing.ala.util import util
from dateutil.parser import parse
from datetime import date, timedelta
from django.db import connection, reset_queries

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('date', nargs='?', type=parse, default=None)

    def handle(self, *args, **options):

        stations = util.get_or_create_stations()
        day = options['date']
        if day == None:
            day = date.today() - timedelta(1)

        try:
            # util.load(stations[0], day)
            # reset_queries()
            # util.create_avgs(stations[0], day)
            for station in stations:
                util.load(station, day)
                util.create_avgs(station, day)
        except Exception as e:
            # for q in connection.queries:
            #     print(q['sql'])
            self.stdout.write(self.style.ERROR(e))
