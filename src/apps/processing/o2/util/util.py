# coding=utf-8
import requests
from contextlib import closing

from apps.common import models as common_models
from apps.utils.obj import *
from apps.utils.time import UTC_P0100
from apps.processing.o2.models import Zsj, MobilityStream, \
    OCCURRENCE_CHOICES, UNIQUES_CHOICES, MobilityObservation, ANY_OCCURRENCE, \
    SocioDemoObservation, MALE_GENDER, FEMALE_GENDER
from apps.common.models import Process, Property
from datetime import timedelta, datetime, time
from dateutil.parser import parse
from django.db.utils import IntegrityError
from itertools import product
from psycopg2.extras import DateTimeTZRange, NumericRange
import logging
import urllib3

from poster.local_settings import O2_API_KEY

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

zsjs_def = [
    ('012386', {'name': u'Líšeň sever'}),
    ('012343', {'name': u'jih'}),
    ('313297', {'name': u'východ'}),
    ('012459', {'name': u'Velká Klajdovka'}),
    ('012378', {'name': u'Kubelíkova'}),
    ('012335', {'name': u'Trnkova'}),
    ('012408', {'name': u'Líšeň zámek'}),
    ('010022', {'name': u'Zelný trh'}),
    ('010014', {'name': u'Náměstí Svobody'}),
    ('010031', {'name': u'Janáčkovo divadlo'}),
    ('010995', {'name': u'Přízová'}),
    ('313343', {'name': u'Na Svobodné'}),
    ('011380', {'name': u'Červený mlýn'}),
    ('012114', {'name': u'Dolní Heršpice'}),
    ('012149', {'name': u'Přízřenice'}),
    ('012050', {'name': u'Jihlavská, fakultní nemocnice'}),
]

streams_def = (
    # Lisen
    [
        '012386',
        '012343',
        '313297',
        '012459',
        '012378',
        '012335',
        '012408',
    ],
    # shopping malls
    [
        '010022',
        '010014',
        '010031',
        '010995',
        '313343',
        '011380',
        '012114',
        '012149',
        '012050',
    ]
)

props_def = [
    ('mobility', {"name": 'mobility', 'unit': ''}),
    ('population', {"name": 'population', 'unit': ''}),
]

processes_def = [
    ('estimation', {'name': 'estimation'}),
]


def get_or_create_zsjs():
    return get_or_create_objs(Zsj, zsjs_def, 'id_by_provider')

def get_or_create_shopping_mall_zsjs():
    shopping_mall_zsj_defs = list(
        filter(lambda d: d[0] in streams_def[1], zsjs_def)
    )
    return get_or_create_objs(Zsj, shopping_mall_zsj_defs, 'id_by_provider')

def get_or_create_streams():
    result = []
    for stream_def in product(streams_def[0], streams_def[1]):
        zsj_a = Zsj.objects.get(id_by_provider=stream_def[0])
        zsj_b = Zsj.objects.get(id_by_provider=stream_def[1])
        stream_a, _ = MobilityStream.objects.get_or_create(
            src_zsj=zsj_a, dst_zsj=zsj_b)
        result.append(stream_a)
        stream_b, _ = MobilityStream.objects.get_or_create(
            src_zsj=zsj_b, dst_zsj=zsj_a)
        result.append(stream_b)

        stream_a.opposite = stream_b
        stream_a.save()
        stream_b.opposite = stream_a
        stream_b.save()
    return result


def get_or_create_props():
    return get_or_create_objs(Property, props_def, 'name_id')


def get_or_create_processes():
    return get_or_create_objs(Process, processes_def, 'name_id')


def get_or_create_common_props():
    return get_or_create_objs(common_models.Property, props_def, 'name_id')


def get_or_create_common_processes():
    return get_or_create_objs(common_models.Process, processes_def, 'name_id')


def load_mobility(streams):
    """Returns False if HTTP Error 429 was encountered, otherwise True."""
    phenomenon_time = None

    payload = {
        'apikey': O2_API_KEY
    }
    # url = 'https://developer.o2.cz/mobility/sandbox/api/info/'
    url = 'https://developer.o2.cz/mobility/api/info'
    with closing(requests.get(url, params=payload, verify=False)) as info_r:
        if (info_r.status_code == 200):

            phenomenon_time = parse(
                info_r.json()['backendDataFrom']
            ).replace(tzinfo=UTC_P0100)
        elif (info_r.status_code == 429):
            logger.info('O2 Liberty API encountered HTTP Error 429 '
                        '"Too Many Requests"')
            return False
        else:
            logger.error('O2 Liberty API HTTP Error {} for {}'.format(
                info_r.status_code, url))
            raise ValueError('O2 Liberty API HTTP Error {} for {}'.format(
                info_r.status_code, url))

    if phenomenon_time is None:
        raise ValueError('O2 unknown phenomenon time')

    logger.info('Phenomenon date of mobility observations: {0}'.format(
        phenomenon_time.strftime('%Y-%m-%d')))


    def pt_to_range(phenomenon_time):
        pt_range = DateTimeTZRange(
            phenomenon_time,
            phenomenon_time + timedelta(1)
        )
        return pt_range

    pt_range = pt_to_range(phenomenon_time)

    get_or_create_props()
    observed_property = Property.objects.get(name_id='mobility')
    get_or_create_processes()
    procedure = Process.objects.get(name_id='estimation')

    # use only applicable and independent occurrence types
    occurrence_types = tuple(filter(lambda occ: occ[0] != ANY_OCCURRENCE,
                                    OCCURRENCE_CHOICES))

    # 126 * 2 * 2 * 2 = 1008
    all_query_defs = list(product(streams, occurrence_types,
                                  occurrence_types, UNIQUES_CHOICES))
    # all_query_defs = all_query_defs[:2]

    def get_obs(query_def):
        try:
            obs = MobilityObservation.objects.get(
                phenomenon_time_range=pt_range,
                observed_property=observed_property,
                procedure=procedure,
                feature_of_interest=query_def[0],
                src_occurrence_type=query_def[1][0],
                dst_occurrence_type=query_def[2][0],
                uniques_type=query_def[3][0],
            )
            if (obs.result_null_reason not in ("", "HTTP Error 204")):
                obs = None
        except MobilityObservation.DoesNotExist:
            obs = None
        return obs

    query_defs = list(filter(lambda qd: get_obs(qd) is None, all_query_defs))

    logger.info("Already loaded {} from {} mobility observations.".format(
        len(all_query_defs) - len(query_defs), len(all_query_defs)))

    if (len(query_defs) == 0):
        return True

    logger.info("Loading next mobility observations")

    loaded_count = 0
    updated_count = 0
    err_429 = False
    for query_def in query_defs:
        feature_of_interest = query_def[0]
        src_zsj = feature_of_interest.src_zsj
        dst_zsj = feature_of_interest.dst_zsj
        src_occurrence_type = query_def[1][0]
        dst_occurrence_type = query_def[2][0]
        uniques_type = query_def[3][0]

        # url = 'https://developer.o2.cz/mobility/sandbox/api/transit' \
        #       '/{}/{}'.format(src_zsj.id_by_provider, dst_zsj.id_by_provider)
        url = 'https://developer.o2.cz/mobility/api/transit' \
              '/{}/{}'.format(src_zsj.id_by_provider, dst_zsj.id_by_provider)
        payload = {
            'fromType': src_occurrence_type,
            'toType': dst_occurrence_type,
            'uniques': uniques_type,
            'apikey': O2_API_KEY
        }
        with closing(requests.get(url, params=payload, verify=False)) as \
                mob_r:
            if (mob_r.status_code == 200):
                try:
                    res_json = mob_r.json()
                    if 'count' not in res_json:
                        result = None
                        result_null_reason = \
                            'missing "count" key in response JSON'
                    elif res_json['count'] is None:
                        result = None
                        result_null_reason = \
                            '"count" set to null'
                    else:
                        result = int(res_json['count'])
                        result_null_reason = ''
                except ValueError as e:
                    result = None
                    result_null_reason = 'invalid JSON in HTTP response'
            elif (mob_r.status_code == 429):
                logger.info('O2 Liberty API encountered HTTP Error 429 '
                            '"Too Many Requests"')
                err_429 = True
                break
            else:
                if (mob_r.status_code != 204):
                    logger.error(
                        'O2 Liberty API HTTP Error {} for {} {}'.format(
                            mob_r.status_code,
                            url,
                            {k: payload[k] for k in payload if k != 'apikey'}
                        )
                    )
                result = None
                result_null_reason = 'HTTP Error {}'.format(mob_r.status_code)

        obs, created = MobilityObservation.objects.get_or_create(
            phenomenon_time_range=pt_range,
            observed_property=observed_property,
            feature_of_interest=feature_of_interest,
            procedure=procedure,
            src_occurrence_type=src_occurrence_type,
            dst_occurrence_type=dst_occurrence_type,
            uniques_type=uniques_type,
            defaults={
                'result': result,
                'result_null_reason': result_null_reason,
            }
        )
        # update existing observation
        if created:
            loaded_count += 1
        else:
            obs.result = result
            obs.result_null_reason = result_null_reason
            obs.save()
            updated_count += 1
    logger.info("Loaded {} and updated {} mobility observations.".format(
        loaded_count, updated_count))
    return not err_429


def load_sociodemo(zsjs):
    """Returns False if HTTP Error 429 was encountered, otherwise True."""
    # https://developer.o2.cz/portal/doc/sociodemo
    phenomenon_date = None

    payload = {
        'apikey': O2_API_KEY
    }
    # url = 'https://developer.o2.cz/sociodemo/sandbox/api/info'
    url = 'https://developer.o2.cz/sociodemo/api/info'
    with closing(requests.get(url, params=payload, verify=False)) as info_r:
        if (info_r.status_code == 200):

            phenomenon_date = parse(
                info_r.json()['backendDataFrom']
            ).replace(tzinfo=UTC_P0100)
        elif (info_r.status_code == 429):
            logger.info('O2 Liberty API encountered HTTP Error 429 '
                        '"Too Many Requests"')
            return False
        else:
            logger.error('O2 Liberty API HTTP Error {} for {}'.format(
                info_r.status_code, url))
            raise ValueError('O2 Liberty API HTTP Error {} for {}'.format(
                info_r.status_code, url))

    if phenomenon_date is None:
        raise ValueError('O2 unknown phenomenon date')

    logger.info('Phenomenon date of socio-demo observations: {}'.format(
        phenomenon_date.strftime('%Y-%m-%d')))

    get_or_create_common_props()
    observed_property = common_models.Property.objects.get(
        name_id='population')
    get_or_create_common_processes()
    procedure = common_models.Process.objects.get(name_id='estimation')

    age_types = list(map(lambda v: str(v), range(1, 6)))

    def age_type_to_range(age_type):
        # (1: 8-18, 2: 19-25, 3: 26-35, 4: 36-55, 5: 56+)
        result = None
        if(age_type=="1"):
            result = NumericRange(8, 18, '[]')
        elif(age_type=="2"):
            result = NumericRange(19, 25, '[]')
        elif(age_type=="3"):
            result = NumericRange(26, 35, '[]')
        elif(age_type=="4"):
            result = NumericRange(36, 55, '[]')
        elif(age_type=="5"):
            result = NumericRange(56, None, '[)')
        return result

    # use only applicable occurrence types
    occurrence_types = tuple(filter(lambda occ: occ[0] != ANY_OCCURRENCE,
                                    OCCURRENCE_CHOICES))

    def gender_value_to_type(gender_value):
        result = None
        if(gender_value=="1"):
            result = MALE_GENDER
        elif(gender_value=="2"):
            result = FEMALE_GENDER
        return result

    gender_values = ["1", "2"]

    hours = list(map(lambda v: str(v), range(0, 24, 2)))

    def hour_to_pt_range(hour):
        time_from = time(int(hour))
        pt_from = datetime.combine(
            phenomenon_date.date(), time_from).replace(tzinfo=UTC_P0100)
        pt_range = DateTimeTZRange(pt_from, pt_from + timedelta(hours=1))
        return pt_range

    age_gender_types = list(map(
        lambda age_type: {
            'url-path': 'age',
            'url-params': {
                'ageGroup': age_type
            },
            'obs-props': {
                'age': age_type_to_range(age_type),
                'gender': '-'
            }
        },
        age_types
    )) + list(map(
        lambda gender_value: {
            'url-path': 'gender',
            'url-params': {
                'g': gender_value
            },
            'obs-props': {
                'gender': gender_value_to_type(gender_value),
                'age': NumericRange(0, None, '[)')
            }
        },
        gender_values
    ))

    # 9 * 5 * 2 * 12 = 1080
    # 9 * 2 * 2 * 12 = 432
    # 1008 + 1080 + 432 = 2520 observations per week
    # 98 * 5 * 6 = 2940 possible requests per week
    all_query_defs = list(product(zsjs, age_gender_types,
                                  occurrence_types, hours))
    # all_query_defs = all_query_defs[:2]

    def get_obs(query_def):
        obs_props = {
            'phenomenon_time_range': hour_to_pt_range(query_def[3]),
            'observed_property': observed_property,
            'procedure': procedure,
            'feature_of_interest': query_def[0],
            'occurrence_type': query_def[2][0],
        }
        obs_props.update(query_def[1]['obs-props'])
        try:
            obs = SocioDemoObservation.objects.get(**obs_props)
            if (obs.result_null_reason not in ("", "HTTP Error 204")):
                obs = None
        except SocioDemoObservation.DoesNotExist:
            obs = None
        return obs

    query_defs = list(filter(lambda qd: get_obs(qd) is None, all_query_defs))

    logger.info("Already loaded {} from {} socio-demo observations.".format(
        len(all_query_defs) - len(query_defs), len(all_query_defs)))

    if (len(query_defs) == 0):
        return True

    logger.info("Loading next socio-demo observations")

    loaded_count = 0
    updated_count = 0
    err_429 = False
    for query_def in query_defs:
        zsj = query_def[0]
        age_gender_type = query_def[1]
        occurrence_type = query_def[2][0]
        hour = query_def[3]

        # 'https://developer.o2.cz/sociodemo/sandbox/api
        url = 'https://developer.o2.cz/sociodemo/api/{}' \
              '/{}'.format(age_gender_type['url-path'], zsj.id_by_provider)
        payload = {
            'occurenceType': occurrence_type,
            'hour': hour,
            'apikey': O2_API_KEY
        }
        payload.update(age_gender_type['url-params'])
        with closing(requests.get(url, params=payload, verify=False)) as \
                soc_r:
            if (soc_r.status_code == 200):
                try:
                    res_json = soc_r.json()
                    if 'count' not in res_json:
                        result = None
                        result_null_reason = \
                            'missing "count" key in response JSON'
                    elif res_json['count'] is None:
                        result = None
                        result_null_reason = \
                            '"count" set to null'
                    else:
                        result = int(res_json['count'])
                        result_null_reason = ''
                except ValueError as e:
                    result = None
                    result_null_reason = 'invalid JSON in HTTP response'
            elif (soc_r.status_code == 429):
                logger.info('O2 Liberty API encountered HTTP Error 429 '
                            '"Too Many Requests"')
                err_429 = True
                break
            else:
                if (soc_r.status_code != 204):
                    logger.error(
                        'O2 Liberty API HTTP Error {} for {} {}'.format(
                            soc_r.status_code,
                            url,
                            {k: payload[k] for k in payload if k != 'apikey'}
                        )
                    )
                result = None
                result_null_reason = 'HTTP Error {}'.format(soc_r.status_code)

        pt_range = hour_to_pt_range(hour)

        ctor_args = {
            'phenomenon_time_range': pt_range,
            'observed_property': observed_property,
            'feature_of_interest': zsj,
            'procedure': procedure,
            'occurrence_type': occurrence_type,
            'defaults': {
                'result': result,
                'result_null_reason': result_null_reason,
            }
        }
        ctor_args.update(age_gender_type['obs-props'])
        obs, created = SocioDemoObservation.objects.get_or_create(**ctor_args)
        # update existing observation
        if created:
            loaded_count += 1
        else:
            obs.result = result
            obs.result_null_reason = result_null_reason
            obs.save()
            updated_count += 1
    logger.info("Loaded {} and updated {} socio-demo observations.".format(
        loaded_count, updated_count))
    return not err_429
