import logging

from django.core.management.base import BaseCommand

from apps.importing.models import ProviderLog

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "fix possible b'' stored strings"

    def handle(self, *args, **options):

        self.stdout.write("Starting to fix the things!")
        i = 0
        for log in ProviderLog.objects.filter(body__startswith="b'", body__endswith="'"):
            if log.body.startswith("b'") and log.body.endswith("'"):
                log.body = eval(log.body).decode("utf-8")
                log.save()
                i += 1
        self.stdout.write("I've fixed {} things".format(i))
