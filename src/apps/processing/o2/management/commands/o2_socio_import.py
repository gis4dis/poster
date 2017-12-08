import logging
from django.core.management.base import BaseCommand, CommandError
from apps.processing.o2.util import util
from django.db import connection, reset_queries

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import O2 socio-demo'

    def handle(self, *args, **options):

        zsjs = util.get_or_create_shopping_mall_zsjs()

        logger.info('Importing socio-demo observations of {} ZSJs '
                    'from O2 Liberty API.'.format(len(zsjs)))

        try:
            util.load_sociodemo(zsjs)
        except Exception as e:
            # for q in connection.queries:
            #     print(q['sql'])
            self.stdout.write(self.style.ERROR(e))
