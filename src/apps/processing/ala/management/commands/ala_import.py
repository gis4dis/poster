import csv
import requests
import codecs
import pytz
from dateutil.parser import parse
from django.db.utils import IntegrityError
from decimal import Decimal
from apps.processing.ala.models import SamplingFeature, Property, Observation
from contextlib import closing
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)
    #
    def handle(self, *args, **options):
        station_name = u'Brno, botanická zahrada PřF MU'
        station_id = '11359201';
        url = 'http://a.la-a.la/chart/data_csvcz.php?probe='+station_id+'&t1=1485914400&t2=1486519200'
        station, _ = SamplingFeature.objects.get_or_create(provider_id=station_id, defaults={"name": station_name})

        all_props = [
            ('precipitation',{"title":'srazky','unit':'mm'}),
        ]

        dbprops = []
        for prop_def in all_props:
            prop,_ = Property.objects.get_or_create(name_id=prop_def[0], defaults=prop_def[1])
            dbprops.append(prop)


        with closing(requests.get(url, stream=True)) as r:
            reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'), delimiter=';')
            for row in reader:
                time = pytz.utc.localize(parse(row[0]))
                for idx,prop in enumerate(dbprops, 1):
                    try:
                        obs = Observation.objects.create(
                            phenomenon_time=time,
                            observed_property=prop,
                            feature_of_interest=station,
                            result=Decimal(row[idx].replace(',','.'))
                        )
                    except IntegrityError as e:
                        self.stdout.write(self.style.ERROR(e))
                # self.stdout.write(self.style.SUCCESS(row))
