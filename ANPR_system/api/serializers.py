from rest_framework import serializers
from .models import *

class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = '__all__'


class DetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detection
        fields = '__all__'
        extra_kwargs = {
            'image_path': {'required': False, 'allow_null': True},
            'video_path': {'required': False, 'allow_null': True},
            'camera': {'required': False, 'allow_null': True},
        }

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image_path:
            return request.build_absolute_uri(f"/{obj.image_path}")
        return None

    def get_video_url(self, obj):
        request = self.context.get("request")
        if obj.video_path:
            return request.build_absolute_uri(f"/{obj.video_path}")
        return None

class BlacklistSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlackList
        fields = '__all__'