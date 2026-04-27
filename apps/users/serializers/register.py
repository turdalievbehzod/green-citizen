from datetime import timedelta
from django.utils import timezone

import phonenumbers
from rest_framework import serializers

from apps.shared.exceptions.custom_exceptions import CustomException
from apps.shared.models import Language
from apps.users.models.users import User, VerificationCode
from apps.users.utils.generate_password import generate_password


class RegisterSerializer(serializers.ModelSerializer):
    language = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['phone_number', 'language']

    @staticmethod
    def validate_phone_number(phone_number):
        try:
            parsed = phonenumbers.parse(phone_number, None)
        except phonenumbers.NumberParseException:
            raise CustomException(
                message_key="INVALID_PHONE_NUMBER_FORMAT"
            )

        if not phonenumbers.is_valid_number(parsed):
            raise CustomException(
                message_key="INVALID_PHONE_NUMBER_FORMAT"
            )

        # User has with this kind of phone number already exists
        if User.objects.filter(
                phone_number=phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.E164)).exists():
            raise CustomException(
                message_key="PHONE_NUMBER_EXIST_ERROR"
            )

        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

    @staticmethod
    def validate_language(language):
        if language not in Language.values:
            raise CustomException(
                message_key="INVALID_LANGUAGE_TYPE"
            )
        return language

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')
        language = validated_data.get('language', Language.EN)
        password = generate_password()
        user = User.objects.create_user(
            phone_number=phone_number, password=password, language=language
        )
        return user
    
class VerifyCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    code = serializers.CharField(required=True)
    
    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        code = attrs.get("code")
        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            raise CustomException(
                message_key="USER_NOT_FOUND"
            )
        verification = VerificationCode.objects.filter(user=user, code=code).first()
        if not verification:
            raise CustomException(
                message_key="INVALID_VERIFICATION_CODE"
            )
        expires_at = verification.created_at + timedelta(
            seconds=verification.expiration_seconds
        )
        if timezone.now() > expires_at:
            verification.delete()
            raise CustomException(message_key="VERIFICATION_CODE_EXPIRED")
        
        verification.delete()
        
        if not user.is_active:
            user.is_active = True
            user.save()
            
        attrs["user"] = user
        
        return attrs
    
class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone_number = attrs["phone_number"]
        password = attrs["password"]

        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            raise CustomException(message_key="USER_NOT_FOUND")

        if not user.check_password(password):
            raise CustomException(message_key="INVALID_CREDENTIALS")

        if not user.is_active:
            raise CustomException(message_key="USER_NOT_VERIFIED")

        attrs["user"] = user
        return attrs
    
class ResendVerificationCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate(self, attrs):
        phone_number = attrs["phone_number"]

        user = User.objects.filter(phone_number=phone_number).first()
        if not user:
            raise CustomException(message_key="USER_NOT_FOUND")

        attrs["user"] = user
        return attrs

class SetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise CustomException(message_key="PASSWORDS_DO_NOT_MATCH")

        user = User.objects.filter(phone_number=attrs["phone_number"]).first()
        if not user:
            raise CustomException(message_key="USER_NOT_FOUND")

        attrs["user"] = user
        return attrs

    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["password1"])
        user.save()
        return user

class UpdatePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password1 = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user

        if not user.check_password(attrs["old_password"]):
            raise CustomException(message_key="INVALID_OLD_PASSWORD")

        if attrs["new_password1"] != attrs["new_password2"]:
            raise CustomException(message_key="PASSWORDS_DO_NOT_MATCH")

        attrs["user"] = user
        return attrs

    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password1"])
        user.save()
        return user

class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "phone_number",
            "first_name",
            "last_name",
            "middle_name",
            "language",
        ]

class UpdatePhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate(self, attrs):
        phone_number = attrs["phone_number"]

        if User.objects.filter(phone_number=phone_number).exists():
            raise CustomException(message_key="PHONE_NUMBER_EXIST_ERROR")

        attrs["phone_number"] = phone_number
        return attrs

class VerifyUpdateCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()

    def validate(self, attrs):
        user = self.context["request"].user

        verification = VerificationCode.objects.filter(
            user=user,
            code=attrs["code"]
        ).first()

        if not verification:
            raise CustomException(message_key="INVALID_VERIFICATION_CODE")

        expires_at = verification.created_at + timedelta(
            seconds=verification.expiration_seconds
        )

        if timezone.now() > expires_at:
            verification.delete()
            raise CustomException(message_key="VERIFICATION_CODE_EXPIRED")

        verification.delete()

        attrs["user"] = user
        return attrs

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "middle_name",
            "language",
        ]