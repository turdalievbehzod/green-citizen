from rest_framework import serializers

from apps.users.models.device import Device


class UserDeviceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            'device_id', 'device_type', 'device_model',
            'operation_version', 'ip_address', 'visit_location',
            'language', 'theme', 'refresh_token_jti',
            'refresh_token_expires_at', 'firebase_token',
            'app_version'
        ]


class UserDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            'id', 'uuid', 'created_at', 'updated_at',
            'device_id', 'device_type', 'device_model',
            'operation_version', 'last_login', 'app_version'
        ]