# Generated by Django 2.1.5 on 2019-03-25 14:08

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('ala', '0013_add_timeslots_delete_unique'),
    ]

    operations = [
        migrations.RunSQL("""
        	DELETE FROM ala_observation_related_observations 
				WHERE from_observation_id IN (
				    SELECT id FROM ala_observation WHERE procedure_id IN (
				        SELECT id FROM common_process WHERE name_id IN (
				            'apps.common.aggregate.sum_total', 
				            'apps.common.aggregate.circle_mean', 
				            'apps.common.aggregate.arithmetic_mean', 
				            'avg_day',
				            'avg_hour'
				        )
				    )
				);
        """),
        migrations.RunSQL("""
        	DELETE FROM ala_observation_related_observations 
				WHERE to_observation_id IN (
				    SELECT id FROM ala_observation WHERE procedure_id IN (
				        SELECT id FROM common_process WHERE name_id IN (
				            'apps.common.aggregate.sum_total', 
				            'apps.common.aggregate.circle_mean', 
				            'apps.common.aggregate.arithmetic_mean', 
				            'avg_day',
				            'avg_hour'
				        )
				    )
				);
        """),
        migrations.RunSQL("""
        	DELETE FROM ala_observation WHERE procedure_id IN (
			    SELECT id FROM common_process WHERE name_id IN (
			        'apps.common.aggregate.sum_total', 
			        'apps.common.aggregate.circle_mean', 
			        'apps.common.aggregate.arithmetic_mean', 
			        'avg_day',
			        'avg_hour'
			    )
			);
        """),
        migrations.RunSQL("""
        	CREATE UNIQUE INDEX ala_observation_uniq ON ala_observation
			    (
			        phenomenon_time_range, 
			        observed_property_id, 
			        feature_of_interest_id, 
			        procedure_id, 
			        COALESCE(time_slots_id, -1)
			    );
        """),
    ]
