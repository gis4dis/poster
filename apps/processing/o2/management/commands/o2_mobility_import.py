import logging
from django.core.management.base import BaseCommand, CommandError
from apps.processing.o2.util import util
from django.db import connection, reset_queries

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import O2 mobility'

    def handle(self, *args, **options):

        util.get_or_create_zsjs()
        streams = util.get_or_create_streams()

        logger.info('Importing mobility observations of {} mobility streams '
                    'from O2 Liberty API.'.format(len(streams)))

        try:
            util.load_mobility(streams)
        except Exception as e:
            # for q in connection.queries:
            #     print(q['sql'])
            self.stdout.write(self.style.ERROR(e))
