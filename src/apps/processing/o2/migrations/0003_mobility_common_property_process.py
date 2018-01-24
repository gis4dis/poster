# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.contrib.postgres.fields.ranges
from django.db import migrations, models
import django.db.models.deletion
from psycopg2.extras import DateTimeTZRange


def correct_data_from_sql():
    sql_statements = """
BEGIN;

LOCK TABLE public.o2_process IN EXCLUSIVE MODE;
LOCK TABLE public.o2_mobilityobservation IN EXCLUSIVE MODE;

ALTER TABLE public.o2_mobilityobservation DROP CONSTRAINT o2_mobilityobservation_procedure_id_bca5bf25_fk_o2_process_id;

ALTER TABLE public.o2_mobilityobservation
  ADD CONSTRAINT o2_mobilityobservation_procedure_id_bca5bf25_fk_o2_process_id FOREIGN KEY (procedure_id)
      REFERENCES public.o2_process (id) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
END;

BEGIN;

LOCK TABLE public.o2_process IN EXCLUSIVE MODE;
LOCK TABLE public.o2_mobilityobservation IN EXCLUSIVE MODE;

UPDATE public.o2_process as A
SET id = B.id
FROM public.common_process as B
WHERE A.name_id = B.name_id;
END;

BEGIN;

LOCK TABLE public.o2_process IN EXCLUSIVE MODE;
LOCK TABLE public.o2_mobilityobservation IN EXCLUSIVE MODE;

ALTER TABLE public.o2_mobilityobservation DROP CONSTRAINT o2_mobilityobservation_procedure_id_bca5bf25_fk_o2_process_id;

ALTER TABLE public.o2_mobilityobservation
  ADD CONSTRAINT o2_mobilityobservation_procedure_id_bca5bf25_fk_o2_process_id FOREIGN KEY (procedure_id)
      REFERENCES public.o2_process (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
END;


BEGIN;

LOCK TABLE public.o2_property IN EXCLUSIVE MODE;
LOCK TABLE public.o2_mobilityobservation IN EXCLUSIVE MODE;

ALTER TABLE public.o2_mobilityobservation DROP CONSTRAINT o2_mobilityobservati_observed_property_id_df4e46f9_fk_o2_proper;
ALTER TABLE public.o2_mobilityobservation
  ADD CONSTRAINT o2_mobilityobservati_observed_property_id_df4e46f9_fk_o2_proper FOREIGN KEY (observed_property_id)
      REFERENCES public.o2_property (id) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
END;

BEGIN;

LOCK TABLE public.o2_property IN EXCLUSIVE MODE;
LOCK TABLE public.o2_mobilityobservation IN EXCLUSIVE MODE;

UPDATE public.o2_property as A
SET id = B.id
FROM public.common_property as B
WHERE A.name_id = B.name_id;
END;

BEGIN;

LOCK TABLE public.o2_property IN EXCLUSIVE MODE;
LOCK TABLE public.o2_mobilityobservation IN EXCLUSIVE MODE;

ALTER TABLE public.o2_mobilityobservation DROP CONSTRAINT o2_mobilityobservati_observed_property_id_df4e46f9_fk_o2_proper;

ALTER TABLE public.o2_mobilityobservation
  ADD CONSTRAINT o2_mobilityobservati_observed_property_id_df4e46f9_fk_o2_proper FOREIGN KEY (observed_property_id)
      REFERENCES public.o2_property (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
END;

"""
    return sql_statements


def ignore_data_from_sql():
    return ''


def update_phenomenon_time_range():
    sql_statements = """
BEGIN;
update o2_mobilityobservation
set phenomenon_time_range=tstzrange(phenomenon_time, phenomenon_time_to, '[]')
where phenomenon_time = phenomenon_time_to;
update o2_mobilityobservation
set phenomenon_time_range=tstzrange(phenomenon_time, phenomenon_time_to, '[)')
where phenomenon_time != phenomenon_time_to;
END;
"""
    return sql_statements


class Migration(migrations.Migration):

    dependencies = [
        ('o2', '0002_sociodemo'),
        ('common', '0003_o2_mobility_properties_processes'),
    ]

    operations = [
        migrations.RunSQL(correct_data_from_sql(), ignore_data_from_sql()),
        migrations.AlterField(
            model_name='mobilityobservation',
            name='observed_property',
            field=models.ForeignKey(editable=False, help_text='Phenomenon that was observed, e.g. air temperature.', on_delete=django.db.models.deletion.CASCADE, related_name='o2_mobilityobservation_related', to='common.Property'),
        ),
        migrations.AlterField(
            model_name='mobilityobservation',
            name='procedure',
            field=models.ForeignKey(editable=False, help_text='Process used to generate the result, e.g. measurement or average.', on_delete=django.db.models.deletion.CASCADE, related_name='o2_mobilityobservation_related', to='common.Process'),
        ),
        migrations.DeleteModel(
            name='Process',
        ),
        migrations.DeleteModel(
            name='Property',
        ),

        migrations.AddField(
            model_name='mobilityobservation',
            name='phenomenon_time_range',
            field=django.contrib.postgres.fields.ranges.DateTimeRangeField(default=DateTimeTZRange(),
                                                                           help_text='Datetime range when the observation was captured.'),
        ),
        migrations.RunSQL(update_phenomenon_time_range()),
        migrations.AlterModelOptions(
            name='mobilityobservation',
            options={'get_latest_by': 'phenomenon_time_range',
                     'ordering': [
                         '-phenomenon_time_range',
                         'feature_of_interest',
                         'procedure',
                         'observed_property',
                         'src_occurrence_type',
                         'dst_occurrence_type',
                         'uniques_type'
                     ]},
        ),
        migrations.AlterUniqueTogether(
            name='mobilityobservation',
            unique_together=set([(
                'phenomenon_time_range',
                'observed_property',
                'feature_of_interest',
                'procedure',
                'src_occurrence_type',
                'dst_occurrence_type',
                'uniques_type'
            )]),
        ),
        migrations.RemoveField(
            model_name='mobilityobservation',
            name='phenomenon_time',
        ),
        migrations.RemoveField(
            model_name='mobilityobservation',
            name='phenomenon_time_to',
        ),
    ]
