# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from apps.common.models import Property, Process
from apps.utils.obj import get_or_create_objs

props_def = [
    ('mobility', {"name": 'mobility', 'unit': ''}),
    ('population', {"name": 'population', 'unit': ''}),
]

processes_def = [
    ('estimation', {'name': 'estimation'}),
]


def load_data(apps, schema_editor):
    # this part of migration was needed when we migrated properties in production DB from o2 to common
    # now it is broken, because common.Property have extra column default_mean
    # get_or_create_objs(Property, props_def, 'name_id')
    # get_or_create_objs(Process, processes_def, 'name_id')
    pass


def delete_data(apps, schema_editor):

    Property_model = apps.get_model("common", "Property")
    Property_model.objects.all().delete()

    Process_model = apps.get_model("common", "Process")
    Process_model.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_ala_properties_processes'),
    ]

    operations = [
        migrations.RunPython(load_data, delete_data),
        # migrations.RunPython(load_properties, delete_properties),
    ]
