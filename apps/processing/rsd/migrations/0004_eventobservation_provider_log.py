# Generated by Django 2.0.3 on 2018-06-09 13:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('importing', '0004_auto_20180214_0043'),
        ('rsd', '0003_categorycustomgroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventobservation',
            name='provider_log',
            field=models.ForeignKey(help_text='Reference to original provider log', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='rsd_event_observation', to='importing.ProviderLog'),
        ),
    ]