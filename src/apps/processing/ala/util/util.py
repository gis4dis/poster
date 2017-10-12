import csv
import requests
from datetime import date, timedelta, datetime
from dateutil.parser import parse
from decimal import Decimal
from contextlib import closing
import codecs
from django.db.utils import IntegrityError
from django.db.models import F, Q
from apps.processing.ala.models import SamplingFeature, Property, Observation, Process
from apps.processing.ala.common import UTC_P0100

stations_def = [
    ('11359201',{'name': u'Brno, botanical garden PřF MU'}),
    ('11359196',{'name': u'Brno, Kraví Hora'}),
    ('11359205',{'name': u'Brno, FF MU, Arne Nováka'}),
    ('11359192',{'name': u'Brno, Schodová'}),
    ('11359202',{'name': u'Brno, Hroznová'}),
    ('11359132',{'name': u'Brno, Mendlovo nám.'}),
]

props_def = [
    ('precipitation',{"name":'precipitation','unit':'mm'}),
    ('air_temperature',{"name":'air temperature','unit':'°C'}),
    ('air_humidity',{"name":'air humidity','unit':'?'}),
    ('ground_air_temperature',{"name":'ground air temperature','unit':'°C'}),
    ('soil_temperature',{"name":'soil temperature','unit':'°C'}),
    ('power_voltage',{"name":'power voltage','unit':'V'}),
]

props_to_provider_idx = {
    'precipitation': 1,
    'air_temperature': 2,
    'air_humidity': 3,
    'ground_air_temperature': 6,
    'soil_temperature': 7,
    'power_voltage': 8,
}

processes_def = [
    ('measure',{'name': u'measuring'}),
    ('avg_hour',{'name': u'hourly average'}),
    ('avg_day',{'name': u'daily average'}),
]

def get_or_create_obj(the_class, obj_def, unique_attr):
    goc_args = {
        unique_attr: obj_def[0],
        'defaults': obj_def[1],
    }
    obj,_ = the_class.objects.get_or_create(**goc_args)
    return obj

def get_or_create_objs(the_class, objs_def, unique_attr):
    objs_map = map(lambda obj_def: get_or_create_obj(the_class, obj_def, unique_attr), objs_def)
    return list(objs_map)

def Q_phenomenon_time(from_aware, to_aware):
    """Return filter of phenomenon_time with instant/period logic."""
    return Q(phenomenon_time__gte=from_aware) & (
            Q(phenomenon_time_to__lt=to_aware) | (
                Q(phenomenon_time_to=to_aware) &
                ~Q(phenomenon_time_to=F('phenomenon_time'))
            )
        )

def get_or_create_stations():
    return get_or_create_objs(SamplingFeature, stations_def, 'id_by_provider')

def get_or_create_props():
    return get_or_create_objs(Property, props_def, 'name_id')

def get_or_create_processes():
    return get_or_create_objs(Process, processes_def, 'name_id')

def load(station, day):
    """Load and save ALA observations for given station and date."""
    get_or_create_processes()
    process = Process.objects.get(name_id='measure')

    from_naive = datetime.combine(day, datetime.min.time())
    to_naive = datetime.combine(day + timedelta(1), datetime.min.time())

    from_aware = from_naive.replace(tzinfo=UTC_P0100)
    to_aware = to_naive.replace(tzinfo=UTC_P0100)

    from_s = int(from_aware.timestamp())
    to_s = int(to_aware.timestamp())

    url = 'http://a.la-a.la/chart/data_csvcz.php?probe={}&t1={}&t2={}'.format(station.id_by_provider, from_s, to_s)

    print(url)
    props = get_or_create_props()

    with closing(requests.get(url, stream=True)) as r:
        reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'), delimiter=';')
        rows = list(reader)
        num_rows = len(rows)
        assert num_rows==145, "Expected 145 rows, found %r" % num_rows
        prev_time = None

        for ridx, row in enumerate(rows, 1):
            time = parse(row[0], dayfirst=True).replace(tzinfo=UTC_P0100)
            for prop in props:
                if prev_time == None and prop.name_id == 'precipitation':
                    continue
                if ridx == num_rows and prop.name_id != 'precipitation':
                    continue
                time_from = prev_time if prop.name_id == 'precipitation' else time
                time_to = time
                try:
                    obs = Observation.objects.create(
                        phenomenon_time=time_from,
                        phenomenon_time_to=time_to,
                        observed_property=prop,
                        feature_of_interest=station,
                        procedure=process,
                        result=Decimal(row[props_to_provider_idx[prop.name_id]].replace(',','.'))
                    )
                except IntegrityError as e:
                    pass
            prev_time = time


def create_avgs(station, day):
    """Create hourly averages for given station and date."""
    if(station==None):
        stations = get_or_create_stations()
        station = stations[0]

    from_naive = datetime.combine(day, datetime.min.time())

    props = get_or_create_props()
    measure_process = Process.objects.get(name_id='measure')

    for prop in props:
        from_aware = from_naive.replace(tzinfo=UTC_P0100)

        process = Process.objects.get(name_id='avg_hour')

        for i in range(0,24):
            to_aware = from_aware + timedelta(hours=1)

            obss = Observation.objects.filter(
                Q_phenomenon_time(from_aware, to_aware),
                feature_of_interest=station,
                observed_property=prop,
                procedure=measure_process
            )
            assert len(obss)==6, "Expected 6 values to count hourly average, found %r" % len(obss)
            values = list(map(lambda o: o.result, obss))
            avg = sum(values) / Decimal(len(values))
            try:
                obs = Observation.objects.create(
                    phenomenon_time=from_aware,
                    phenomenon_time_to=to_aware,
                    observed_property=prop,
                    feature_of_interest=station,
                    procedure=process,
                    result=avg
                )
                obs.related_observations.set(obss)
            except IntegrityError as e:
                pass

            from_aware = to_aware
