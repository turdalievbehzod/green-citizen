import phonenumbers
from rest_framework import serializers

from apps.shared.exceptions.custom_exceptions import CustomException
from apps.shared.models import Language
from apps.users.models.users import User
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