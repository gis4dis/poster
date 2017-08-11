from django.core.management.base import BaseCommand, CommandError
from apps.processing.ala.util import util

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)
    #
    def handle(self, *args, **options):
        # try:
            util.load()
        # except Exception as e:
        #     self.stdout.write(self.style.ERROR(e))
