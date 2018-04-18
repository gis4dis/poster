import logging
from django.core.management.base import BaseCommand
from apps.common.models import Process, Property
from apps.processing.ala.models import SamplingFeature, Observation

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'delete all anomaly score'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        process = Process.objects.get(name_id='anomaly')

        Observation.objects.filter(
            procedure=process,
        ).delete()
