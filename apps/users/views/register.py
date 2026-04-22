from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.shared.utils.custom_response import CustomResponse
from apps.users.serializers.register import RegisterSerializer
from apps.users.utils.verification_code import send_verification_code


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return CustomResponse.error(
                request=request,
                errors=str(serializer.errors),
                message_key="VALIDATION_ERROR"
            )
        user = serializer.save()

        # send verification code to the user's phone number
        send_verification_code.delay(user.id)

        tokens = user.get_tokens()
        data = {
            "user": serializer.data,
            "tokens": tokens
        }

        return CustomResponse.success(
            request=request,
            data=data,
            message_key="USER_REGISTERED_SUCCESSFULLY"
        )


class VerifyCodeAPIView(APIView):
    permission_classes = [AllowAny]


class ResendVerificationCodeAPIView(APIView):
    permission_classes = [AllowAny]