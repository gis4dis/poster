from rest_framework import serializers
from apps.common.models import Property, TimeSlots
from apps.mc.models import TimeSeriesFeature
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ('name_id', 'name', 'unit')


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ('name_id', 'name')


class TimeSlotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlots
        fields = ('name_id', 'name')


class TimeSeriesFeatureSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = TimeSeriesFeature
        geo_field = "geometry"
        id_field = "id"
        fields = '__all__'

    def get_properties(self, instance, fields):
        return {
            **{
                'id_by_provider': instance.id_by_provider,
                'name': instance.name,
            },
            **instance.content,
        }

    def unformat_geojson(self, feature):
        attrs = {
            self.Meta.geo_field: feature["geometry"],
            "content": feature["properties"]
        }

        return attrs


class TimeSeriesSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    phenomenon_time_from = serializers.DateTimeField()
    phenomenon_time_to = serializers.DateTimeField()
    value_frequency = serializers.IntegerField()
    value_duration = serializers.IntegerField()
    properties = serializers.ListField()
    feature_collection = TimeSeriesFeatureSerializer(many=True)
