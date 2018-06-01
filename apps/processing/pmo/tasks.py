from __future__ import absolute_import, unicode_literals

from datetime import date, timedelta

from celery.task import task, group
from celery.utils.log import get_task_logger

from django.core.management import call_command

from apps.processing.ala.models import SamplingFeature
from apps.processing.ala.util import util

logger = get_task_logger(__name__)


@task(name="pmo.import")
def import_default(*args):
    try:
        call_command('pmo_import', *args)
    except Exception as e:
        logger.error(e)
