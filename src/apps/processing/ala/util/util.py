import csv
import requests
import pytz
from datetime import date, timedelta, datetime
from dateutil.parser import parse
from decimal import Decimal
from contextlib import closing
import codecs
from django.db.utils import IntegrityError
from apps.processing.ala.models import SamplingFeature, Property, Observation


stations_def = [
    ('11359201',{'name': u'Brno, botanická zahrada PřF MU'}),
    ('11359196',{'name': u'Brno - Kraví Hora'}),
    ('11359205',{'name': u'Brno, Fil. fak. MU, ul. Arne Nováka'}),
    ('11359192',{'name': u'Brno, Schodová ul.'}),
]

props_def = [
    ('precipitation',{"title":'srazky','unit':'mm'}),
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

def get_or_create_stations():
    return get_or_create_objs(SamplingFeature, stations_def, 'provider_id')

def get_or_create_props():
    return get_or_create_objs(Property, props_def, 'name_id')


# def day_to_url(day):
#     stations =
#
#     url = 'http://a.la-a.la/chart/data_csvcz.php?probe='+station.provider_id+'&t1=1485914400&t2=1486519200'

def load():
    stations = get_or_create_stations()
    station = stations[0]

    day = date.today() - timedelta(1)

    from_naive = datetime.combine(day, datetime.min.time())
    to_naive = datetime.combine(day + timedelta(1), datetime.min.time())

    from_utc = pytz.utc.localize(from_naive)
    to_utc = pytz.utc.localize(to_naive)

    from_s = int(from_utc.timestamp())-60*60
    to_s = int(to_utc.timestamp())-60*60



    url = 'http://a.la-a.la/chart/data_csvcz.php?probe={}&t1={}&t2={}'.format(station.provider_id, from_s, to_s)

    print(url)
    props = get_or_create_props()


    with closing(requests.get(url, stream=True)) as r:
        reader = csv.reader(codecs.iterdecode(r.iter_lines(), 'utf-8'), delimiter=';')
        praguetz = pytz.timezone('Europe/Prague')
        for row in reader:
            time = praguetz.localize(parse(row[0], dayfirst=True))
            # for idx,prop in enumerate(props, 1):
            #     try:
            #         obs = Observation.objects.create(
            #             phenomenon_time=time,
            #             observed_property=prop,
            #             feature_of_interest=station,
            #             result=Decimal(row[idx].replace(',','.'))
            #         )
            #     except IntegrityError as e:
            #         pass
