# coding=utf-8
import requests
from contextlib import closing
from apps.processing.common.obj import *
from apps.processing.common.filter import *
from apps.processing.common.time import UTC_P0100
from apps.processing.o2.models import Zsj, MobilityStream, Property, Process, \
    OCCURRENCE_CHOICES, UNIQUES_CHOICES, MobilityObservation, ANY_OCCURRENCE
from datetime import timedelta, datetime
from dateutil.parser import parse
from django.db.utils import IntegrityError
from itertools import product
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
    [
        '012386',
        '012343',
        '313297',
        '012459',
        '012378',
        '012335',
        '012408',
    ],
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
]

processes_def = [
    ('estimation', {'name': 'estimation'}),
]


def get_or_create_zsjs():
    return get_or_create_objs(Zsj, zsjs_def, 'id_by_provider')


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


def load_mobility(streams):
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
            return
        else:
            logger.error('O2 Liberty API HTTP Error {} for {}'.format(
                info_r.status_code, url))
            raise ValueError('O2 Liberty API HTTP Error {} for {}'.format(
                info_r.status_code, url))

    if phenomenon_time is None:
        raise ValueError('O2 unknown phenomenon time')

    phenomenon_time_to = phenomenon_time + timedelta(1)
    logger.info('Phenomenon date: {0}'.format(
        phenomenon_time.strftime('%Y-%m-%d')))

    get_or_create_props()
    observed_property = Property.objects.get(name_id='mobility')
    get_or_create_processes()
    procedure = Process.objects.get(name_id='estimation')

    # use only applicable and independent occurrence types
    occurrence_types = tuple(filter(lambda occ: occ[0] != ANY_OCCURRENCE,
                                    OCCURRENCE_CHOICES))

    all_query_defs = list(product(streams, occurrence_types,
                                  occurrence_types, UNIQUES_CHOICES))

    def get_obs(query_def):
        try:
            obs = MobilityObservation.objects.get(
                Q_phenomenon_time(phenomenon_time, phenomenon_time_to),
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

    logger.info("Already loaded {} from {} observations.".format(
        len(all_query_defs) - len(query_defs), len(all_query_defs)))

    if (len(query_defs) == 0):
        return

    logger.info("Loading next observations")

    loaded_count = 0
    updated_count = 0
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
                result = int(mob_r.json()['count'])
                result_null_reason = ''
            elif (mob_r.status_code == 429):
                logger.info('O2 Liberty API encountered HTTP Error 429 '
                            '"Too Many Requests"')
                break
            else:
                if (mob_r.status_code != 204):
                    logger.error(
                        'O2 Liberty API HTTP Error {} for {} {}'.format(
                            info_r.status_code,
                            url,
                            {k: payload[k] for k in payload if k != 'apikey'}
                        )
                    )
                result = None
                result_null_reason = 'HTTP Error {}'.format(mob_r.status_code)

        obs, created = MobilityObservation.objects.get_or_create(
            phenomenon_time=phenomenon_time,
            phenomenon_time_to=phenomenon_time_to,
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
    logger.info("Loaded {} observations and updated {} observations.".format(
        loaded_count, updated_count))
