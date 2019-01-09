from importlib import import_module

from dateutil import relativedelta
from dateutil.parser import parse
from django.conf import settings
from django.contrib.gis.geos import Polygon
from psycopg2.extras import DateTimeTZRange
from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime

from apps.ad.anomaly_detection import get_timeseries
from apps.common.models import Property, Process
from apps.common.models import Topic
from apps.mc.models import TimeSeriesFeature
from apps.common.models import TimeSeries
from apps.mc.api.serializers import PropertySerializer, TimeSeriesSerializer, TopicSerializer
from apps.utils.time import UTC_P0100
from apps.common.util.util import generate_intervals


def import_models(path):
    provider_module = None
    provider_model = None
    error_message = None
    try:
        path = path.rsplit('.', 1)
        provider_module = import_module(path[0])
        provider_model = getattr(provider_module, path[1])
        return provider_model, provider_module, error_message
    except ModuleNotFoundError as e:
        error_message = 'module not found'
        return provider_model, provider_module, error_message
    except AttributeError as e:
        error_message = 'function not found'
        return provider_model, provider_module, error_message


def parse_date_range(from_string, to_string):
    if from_string:
        try:
            day_from = parse(from_string)
        except ValueError as e:
            raise APIException("Phenomenon_date_from is not valid")

    if to_string:
        try:
            day_to = parse(to_string)
            day_to = day_to + relativedelta.relativedelta(days=1)
        except ValueError as e:
            raise APIException("Phenomenon_date_to is not valid")

    if day_from > day_to:
        raise APIException("Phenomenon_date_from bound must be less than or equal phenomenon_date_to")

    time_range_boundary = '[]' if day_from == day_to else '[)'

    pt_range = DateTimeTZRange(
        day_from, day_to, time_range_boundary)

    return pt_range, day_from, day_to


def float_bbox_param(value):
    try:
        float_val = float(value)
        return float_val
    except:
        raise APIException("BBOX param float conversion error: %s" % value)


def validate_bbox_values(bbox_array):
    if bbox_array[0] >= bbox_array[2]:
        raise APIException("BBOX minx is not < maxx")

    if bbox_array[1] >= bbox_array[3]:
        raise APIException("BBOX miny is not < maxy")


def parse_properties(properties_string):
    properties_parts = properties_string.rsplit(',')
    return properties_parts


def parse_bbox(bbox_string):
    bbox_parts = bbox_string.rsplit(',')

    if len(bbox_parts) != 4:
        raise APIException("BBOX 4 parameters required")

    x_min = float_bbox_param(bbox_parts[0])
    y_min = float_bbox_param(bbox_parts[1])
    x_max = float_bbox_param(bbox_parts[2])
    y_max = float_bbox_param(bbox_parts[3])

    if x_min and y_min and x_max and y_max:
        bbox = (x_min, y_min, x_max, y_max)
        validate_bbox_values(bbox)
        geom_bbox = Polygon.from_bbox(bbox)
    else:
        raise APIException("Error in passed query parameter: bbox")

    return geom_bbox


class PropertyViewSet(viewsets.ViewSet):
    def list(self, request):
        if 'topic' in request.GET:
            topic_param = request.GET['topic']
            topic = settings.APPLICATION_MC.TOPICS.get(topic_param)

            if not topic or not Topic.objects.filter(name_id=topic_param).exists():
                raise APIException('Topic not found.')

            prop_names = list(topic['properties'].keys())

            queryset = Property.objects.filter(name_id__in=prop_names)
            serializer = PropertySerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            raise APIException("Parameter topic is required")


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    topics = settings.APPLICATION_MC.TOPICS.keys()
    queryset = Topic.objects.filter(name_id__in=list(topics))
    serializer_class = TopicSerializer


# http://localhost:8000/api/v2/timeseries/?topic=drought&properties=air_temperature,ground_air_temperature&phenomenon_date_from=2018-01-20&phenomenon_date_to=2018-09-27&bbox=1826997.8501,6306589.8927,1846565.7293,6521189.3651
# http://localhost:8000/api/v2/timeseries?topic=drought&properties=air_temperature,ground_air_temperature&phenomenon_date_from=2018-01-20&phenomenon_date_to=2018-09-27

def get_index_shift(time_slots, first_item_from, current_item_from):
    first_idx = None
    current_idx = None
    for idx in range(len(time_slots)):
        slot = time_slots[idx]
        if slot.lower == first_item_from:
            first_idx = idx
        if slot.lower == current_item_from:
            current_idx = idx

        if first_idx and current_idx:
            break

    return current_idx - first_idx


def get_value_frequency(t, from_datetime):
    to = from_datetime + t.frequency + t.frequency
    result_slots = generate_intervals(
        timeseries=t,
        from_datetime=from_datetime,
        to_datetime=to,
    )

    if len(result_slots) < 2:
        return None

    diff = (result_slots[1].lower - result_slots[0].lower).total_seconds()
    return diff


def get_empty_slots(t, pt_range_z):
    return generate_intervals(
        timeseries=t,
        from_datetime=pt_range_z.lower,
        to_datetime=pt_range_z.upper,
    )


def prepare_data(
        time_slots,
        observed_property,
        observation_provider_model,
        feature_of_interest,
        process):

    obss = observation_provider_model.objects.filter(
        observed_property=observed_property,
        procedure=process,
        feature_of_interest=feature_of_interest,
        phenomenon_time_range__in=time_slots
    )

    obs_reduced = {obs.phenomenon_time_range.lower.timestamp(): obs for obs in obss}

    observations = []
    result_time_range_from = None
    result_time_range_to = None

    last_not_null_index = 0
    for i in range(len(time_slots) -1, -1, -1):
        slot = time_slots[i]
        st = slot.lower.timestamp()
        if st in obs_reduced and obs_reduced[st] and obs_reduced[st].result is not None:
            last_not_null_index = i + 1
            break

    # for slot in time_slots:
    if last_not_null_index > len(time_slots):
        last_not_null_index = len(time_slots)
    for i in range(0, last_not_null_index):
        slot = time_slots[i]
        st = slot.lower.timestamp()
        obs = None

        if st in obs_reduced and obs_reduced[st] and obs_reduced[st].result is not None:
            obs = obs_reduced[st]

        if len(observations) > 0 or obs:
            if obs is None:
                obs = observation_provider_model(
                    phenomenon_time_range=slot,
                    observed_property=observed_property,
                    feature_of_interest=feature_of_interest,
                    procedure=process,
                    result=None
                )
            observations.append(obs)
            result_time_range_to = obs.phenomenon_time_range.upper
            if not result_time_range_from:
                result_time_range_from = obs.phenomenon_time_range.lower

    return {
        'observations': observations,
        'phenomenon_time_range': DateTimeTZRange(
            result_time_range_from,
            result_time_range_to
        )
    }


class TimeSeriesViewSet(viewsets.ViewSet):

    def list(self, request):
        if 'topic' in request.GET:
            topic = request.GET['topic']
        else:
            raise APIException('Parameter topic is required')

        topic_config = settings.APPLICATION_MC.TOPICS.get(topic)

        if not topic_config or not Topic.objects.filter(name_id=topic).exists():
            raise APIException('Topic not found.')

        properties = topic_config['properties']
        ts_config = topic_config['time_series']

        if 'properties' in request.GET:
            properties_string = request.GET['properties']
            param_properties = parse_properties(properties_string)

            for prop in param_properties:
                if not properties.get(prop):
                    raise APIException('Property: ' + prop + ' does not exist in config')

                try:
                    Property.objects.get(name_id=prop)
                except Property.DoesNotExist:
                    raise APIException('Property from config not found.')

        else:
            param_properties = properties.keys()
            db_filtered_props = []
            for prop in param_properties:
                try:
                    Property.objects.get(name_id=prop)
                    db_filtered_props.append(prop)
                except Property.DoesNotExist:
                    raise APIException('Config has property not present in datbaase.')

        if 'phenomenon_date_from' in request.GET:
            phenomenon_date_from = request.GET['phenomenon_date_from']
        else:
            raise APIException("Parameter phenomenon_date_from is required")

        if 'phenomenon_date_to' in request.GET:
            phenomenon_date_to = request.GET['phenomenon_date_to']
        else:
            raise APIException("Parameter phenomenon_date_to is required")

        pt_range, day_from, day_to = parse_date_range(phenomenon_date_from, phenomenon_date_to)

        pt_range_z = DateTimeTZRange(
            pt_range.lower.replace(tzinfo=UTC_P0100),
            pt_range.upper.replace(tzinfo=UTC_P0100)
        )

        zero = parse_datetime(ts_config['zero'])
        frequency = ts_config['frequency']
        range_from = ts_config['range_from']
        range_to = ts_config['range_to']

        t = TimeSeries(
            zero=zero,
            frequency=frequency,
            range_from=range_from,
            range_to=range_to
        )
        t.full_clean()
        t.clean()

        time_slots = get_empty_slots(t, pt_range_z)
        start = pt_range_z.lower
        if start < t.zero:
            start = t.zero
        value_frequency = get_value_frequency(t, zero)
        value_duration = None

        geom_bbox = None
        if 'bbox' in request.GET:
            bbox = request.GET['bbox']
            geom_bbox = parse_bbox(bbox)

        model_props = {}

        if topic_config:
            for prop in param_properties:
                prop_config = properties.get(prop)
                op = prop_config['observation_providers']

                for provider in op:
                    if provider in model_props:
                        model_props[provider].append(prop)
                    else:
                        model_props[provider] = [prop]

        time_series_list = []
        phenomenon_time_from = None
        phenomenon_time_to = None

        for model in model_props:

            provider_module, provider_model, error_message = import_models(model)
            if error_message:
                raise APIException("Importing error - %s : %s" % (model, error_message))

            path = model.rsplit('.', 1)
            provider_module = import_module(path[0])
            provider_model = getattr(provider_module, path[1])

            feature_of_interest_model = provider_model._meta.get_field('feature_of_interest').remote_field.model

            if geom_bbox:
                all_features = feature_of_interest_model.objects.filter(geometry__intersects=geom_bbox)
            else:
                all_features = feature_of_interest_model.objects.all()

            observation_provider_model_name = f"{provider_model.__module__}.{provider_model.__name__}"

            for item in all_features:
                content = {}

                hasValues = False

                f_phenomenon_time_from = None
                f_phenomenon_time_to = None

                for prop in model_props[model]:
                    prop_config = topic_config['properties'][prop]

                    try:
                        process = Process.objects.get(
                            name_id=prop_config['observation_providers'][observation_provider_model_name]["process"])
                    except Process.DoesNotExist:
                        process = None

                    if not process:
                        raise APIException('Process from config not found.')

                    prop_item = Property.objects.get(name_id=prop)

                    data = prepare_data(
                        time_slots=time_slots,
                        observed_property=prop_item,
                        observation_provider_model=provider_model,
                        feature_of_interest=item,
                        process=process
                    )

                    observations = data['observations']

                    if len(observations) > 0 and value_duration is None:
                        value_duration = observations[0].phenomenon_time_range.upper \
                                         - observations[0].phenomenon_time_range.lower
                        value_duration = value_duration.total_seconds()

                    ts = get_timeseries(
                        phenomenon_time_range=data['phenomenon_time_range'],
                        observations=observations
                    )

                    if ts['phenomenon_time_range'].lower is not None:
                        if not phenomenon_time_from or phenomenon_time_from > ts['phenomenon_time_range'].lower:
                            phenomenon_time_from = ts['phenomenon_time_range'].lower

                    if ts['phenomenon_time_range'].upper is not None:
                        if not phenomenon_time_to or phenomenon_time_to > ts['phenomenon_time_range'].upper:
                            phenomenon_time_to = ts['phenomenon_time_range'].upper

                    if ts['phenomenon_time_range'].lower is not None:
                        if not f_phenomenon_time_from or f_phenomenon_time_from > ts['phenomenon_time_range'].lower:
                            f_phenomenon_time_from = ts['phenomenon_time_range'].lower

                    if ts['phenomenon_time_range'].upper is not None:
                        if not f_phenomenon_time_to or f_phenomenon_time_to > ts['phenomenon_time_range'].upper:
                            f_phenomenon_time_to = ts['phenomenon_time_range'].upper

                    feature_prop_dict = {
                        'values': ts['property_values'],
                        'anomaly_rates': ts['property_anomaly_rates'],
                        'phenomenon_time_from': ts['phenomenon_time_range'].lower,
                        'phenomenon_time_to': ts['phenomenon_time_range'].upper,
                        'value_index_shift': None
                    }

                    content[prop] = feature_prop_dict

                    if len(ts['property_values']) > 0:
                        hasValues = True

                feature_id = path[0] + \
                             "." + \
                             feature_of_interest_model.__name__ + \
                             ":" + \
                             str(item.id_by_provider)

                if hasValues:
                    f = TimeSeriesFeature(
                        id=feature_id,
                        id_by_provider=item.id_by_provider,
                        name=item.name,
                        geometry=item.geometry,
                        content=content
                    )
                    time_series_list.append(f)

        for item in time_series_list:
            if phenomenon_time_from:
                for item_prop in item.content:
                    item_prop_from = item.content[item_prop]['phenomenon_time_from']

                    if phenomenon_time_from and item_prop_from:
                        value_index_shift = get_index_shift(time_slots, phenomenon_time_from, item_prop_from)
                        item.content[item_prop]['value_index_shift'] = value_index_shift
                    else:
                        item.content[item_prop]['value_index_shift'] = None

                    try:
                        del item.content[item_prop]['phenomenon_time_from']
                    except KeyError:
                        pass

                    try:
                        del item.content[item_prop]['phenomenon_time_to']
                    except KeyError:
                        pass

        if len(time_series_list) == 0:
            value_frequency = None

        response_data = {
            'phenomenon_time_from': phenomenon_time_from,
            'phenomenon_time_to': phenomenon_time_to,
            'value_frequency': value_frequency,
            'value_duration': value_duration,
            'feature_collection': time_series_list,
            'properties': param_properties
        }

        results = TimeSeriesSerializer(response_data).data
        return Response(results)
