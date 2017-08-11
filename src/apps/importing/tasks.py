from __future__ import absolute_import, unicode_literals
from celery.task import task
import random

@task(name="general.print_debug")
def print_debug(text):
    print(text)
