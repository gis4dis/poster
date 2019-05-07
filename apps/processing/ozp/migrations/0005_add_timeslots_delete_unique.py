# Generated by Django 2.1.5 on 2019-03-26 14:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0008_timeslots'),
        ('ozp', '0004_created_updated_notnull'),
    ]

    operations = [
        migrations.AddField(
            model_name='observation',
            name='time_slots',
            field=models.ForeignKey(default=None, help_text='Time_slots used to calc aggregations', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='ozp_observation_related', to='common.TimeSlots'),
        ),
        migrations.AlterUniqueTogether(
            name='observation',
            unique_together=set(),
        ),
    ]
