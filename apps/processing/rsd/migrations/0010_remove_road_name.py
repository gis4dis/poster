# Generated by Django 2.0.3 on 2018-09-17 17:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rsd', '0009_auto_20180904_1818'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='road',
            name='name',
        ),
    ]
