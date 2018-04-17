import logging
from django.core.management.base import BaseCommand
from apps.processing.ala.util import util
from dateutil.parser import parse
from dateutil import relativedelta
from datetime import date, timedelta
from apps.common.models import Process, Property
from apps.processing.ala.models import SamplingFeature, Observation
from luminol.anomaly_detector import AnomalyDetector
from datetime import datetime
import pytz
import time

logger = logging.getLogger(__name__)

stations_def = ('11359201', '11359196', '11359205', '11359192', '11359202', '11359132')


class Command(BaseCommand):
    help = 'Import data from ALA stations. Optionally you can pass date, ' \
           'otherwise it will fetch the day before yesterday data.'

    def add_arguments(self, parser):
        parser.add_argument('property_name', nargs='*', type=str, default=['air_temperature'])

    def handle(self, *args, **options):
        propertys = options['property_name']
        for station in stations_def:
            for property in propertys:
                user_list_obj = Observation.objects.filter(
                    feature_of_interest=SamplingFeature.objects.get(id_by_provider=station),
                    observed_property=Property.objects.get(name_id=property),
                    procedure=Process.objects.get(name_id='measure')
                ).order_by('phenomenon_time_range')

                #mainpart
                anomalyScore = anomaly_detect(user_list_obj, 'default_detector')
                anomaly_score_save(user_list_obj,anomalyScore)


def anomaly_detect(observation, detector_method='default_detector'):
    results_dic = dict()
    for line in observation:
        results_dic[time.mktime(line.phenomenon_time_range.lower.astimezone(pytz.utc).timetuple())] = float(line.result)

    my_detector = AnomalyDetector(results_dic, None, False, None, None, detector_method, None, None, None)
    anomalies = my_detector.get_anomalies()
    if anomalies:
        time_period = anomalies[0].get_time_window()
    #TODO the anomaly point

    score = my_detector.get_all_scores()

    return list(score.itervalues())


def anomaly_score_save(raw_obss, score):
    anomaly_process = Process.objects.get(name_id='anomaly')

    for i in range(0, len(raw_obss)):
        new_obs = Observation.objects.create(
            phenomenon_time_range=raw_obss[i].phenomenon_time_range,
            observed_property=raw_obss[i].observed_property,
            feature_of_interest=raw_obss[i].feature_of_interest,
            procedure=anomaly_process,
            result=score[i],
            result_null_reason='',
        )
        new_obs.related_observations.set(raw_obss)
    print("Saved successfully")
