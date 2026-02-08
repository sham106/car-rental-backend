from rest_framework import serializers
from .models import Vehicle
import json

class VehicleSerializer(serializers.ModelSerializer):
    gallery = serializers.JSONField(required=False)

    class Meta:
        model = Vehicle
        fields = '__all__'

    def to_representation(self, instance):
        """Convert JSON string back to list for frontend"""
        ret = super().to_representation(instance)
        ret['gallery'] = instance.get_gallery_list()
        return ret

    def create(self, validated_data):
        if 'gallery' in validated_data:
            validated_data['gallery'] = json.dumps(validated_data['gallery'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'gallery' in validated_data:
            validated_data['gallery'] = json.dumps(validated_data['gallery'])
        return super().update(instance, validated_data)