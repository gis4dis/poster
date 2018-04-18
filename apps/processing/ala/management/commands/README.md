# Anomaly Detection
Write by Kaiyue Zang, Jiemin Zhou
 
## Main goal
Finding Outliers in a Time Series

## Requirements
luminol(https://github.com/linkedin/luminol)  
We use a local version modified from 0.4

## Basic functions
+ anomaly_detect  
```
anomaly_detect(list_obss, detector_method='default_detector')
```
*list_obss*:A list of Observation objects made by SELECT code (Sort by time series)  
*detector_method*:The anomaly method you choose, default is "???//TODO"

return:A list of Anomaly Score(same index as _list_obss_)

+ anomaly_score_save
```
anomaly_score_save(list_obss, score)
```
*list_obss*:A list of Observation objects made by SELECT code (Sort by time series)  
*score*:The return value from anomaly_detect()

return: viod  
  
**Example**:
```
list_obss = Observation.objects.filter(
           ...    
           ).order_by('phenomenon_time_range')

#mainpart
anomalyScore = anomaly_detect(list_obss, 'default_detector')
anomaly_score_save(list_obss,anomalyScore)
```

**Notice**:  
_list_obss_ must sort by time series
_anomalies_ is a list inside the anomaly_detect(), 

## Anomaly detection algorithms
???//TODO

## File organize
**Added**:  
+ Local luminol package
+ apps/proyessing/ala/management/commands/anomaly_detection.py  
+ apps/proyessing/ala/management/commands/anomaly_delete.py  
+ apps/proyessing/ala/management/commands/README.md  
**changed**:  
+ apps/processing/ala/util/util.py
