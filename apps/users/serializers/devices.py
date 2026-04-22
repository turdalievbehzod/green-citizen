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

    def validate(self, attrs):
        user = self.context['request'].user

        if Device.objects.filter(
            user=user,
            device_id=attrs.get('device_id'),
            is_active=True
        ).exists():
            raise serializers.ValidationError({
                "device_id": "Device already registered"
            })

        return attrs

    def validate_refresh_token_jti(self, value):
        if Device.objects.filter(refresh_token_jti=value).exists():
            raise serializers.ValidationError("Duplicate token")
        return value

    def validate_firebase_token(self, value):
        if value and Device.objects.filter(firebase_token=value).exists():
            raise serializers.ValidationError("Firebase token already used")
        return value

    def validate_refresh_token_expires_at(self, value):
        from django.utils import timezone
        if value and value <= timezone.now():
            raise serializers.ValidationError("Expiry must be in future")
        return value
    
class UserDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            'id', 'device_id', 'device_type', 'device_model',
            'operation_version', 'ip_address', 'visit_location',
            'language', 'theme', 'refresh_token_jti',
            'refresh_token_expires_at', 'firebase_token',
            'app_version', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
        
    def validate_refresh_token_jti(self, value):
        qs = Device.objects.filter(refresh_token_jti=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError("Duplicate token")
        return value
            
    def validate_firebase_token(self, value):
        if value and Device.objects.filter(firebase_token=value).exists():
            raise serializers.ValidationError("Firebase token already used")
        return value
        
    def validate_refresh_token_expires_at(self, value):
        from django.utils import timezone
        if value and value <= timezone.now():
            raise serializers.ValidationError("Expiry must be in future")
        return value