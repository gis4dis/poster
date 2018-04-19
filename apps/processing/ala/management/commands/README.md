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
*detector_method*:The anomaly method you choose, default is "default_detector", which is a method considered both Exponential Moving Avg and derivative.

return:A list of Anomaly Score(same index as _list_obss_)

+ anomaly_score_save
```
anomaly_score_save(list_obss, score)
```
*list_obss*:A list of Observation objects made by SELECT code (Sort by time series)  
*score*:The return value from anomaly_detect()

return: void  
  
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
_list_obss_ **must** sort by time series  
_anomalies_ is a list inside the anomaly_detect().

## Anomaly detection algorithms
Available algorithms and their additional parameters are:
```
1.  'bitmap_detector': # behaves well for huge data sets.

2.  'default_detector': # it is the default detector, and is good for continuously changing data.

3.  'derivative_detector': # meant to be used when abrupt changes of value are of main interest.

4.  'exp_avg_detector': # meant to be used when values are in a roughly stationary range.
                        # and it is the default refine algorithm.

```
**Notice**:
The four existing algorithms may be not suitable for the anomaly detection of each property. More suitable algorithms will be added in the future work.

## File organize
### Added:  
+ Local luminol package
+ apps/proyessing/ala/management/commands/anomaly_detection.py  
+ apps/proyessing/ala/management/commands/anomaly_delete.py  
+ apps/proyessing/ala/management/commands/README.md  

### changed:  
+ apps/processing/ala/util/util.py
