# Generated by Django 2.1.5 on 2019-03-27 06:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0008_timeslots'),
        ('rsd', '0010_remove_road_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventobservation',
            name='time_slots',
            field=models.ForeignKey(default=None, help_text='Time_slots used to calc aggregations', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='rsd_eventobservation_related', to='common.TimeSlots'),
        ),
        migrations.AddField(
            model_name='numberofeventsobservation',
            name='time_slots',
            field=models.ForeignKey(default=None, help_text='Time_slots used to calc aggregations', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='rsd_numberofeventsobservation_related', to='common.TimeSlots'),
        ),
        migrations.AlterUniqueTogether(
            name='eventobservation',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='numberofeventsobservation',
            unique_together=set(),
        ),
    ]
