# Generated by Django 2.0.3 on 2018-08-08 11:55

from django.db import migrations, models
from django.utils import timezone

class Migration(migrations.Migration):

    dependencies = [
        ('ozp', '0002_created_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='observation',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        )
    ]