from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.shared.utils.custom_response import CustomResponse
from apps.users.serializers.register import LoginSerializer, MeSerializer, ProfileUpdateSerializer, RegisterSerializer, ResendVerificationCodeSerializer, SetPasswordSerializer, UpdatePasswordSerializer, UpdatePhoneSerializer, VerifyCodeSerializer, VerifyUpdateCodeSerializer
from apps.users.utils.verification_code import send_verification_code
from apps.users.views.users import UserSerializer


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
    serializer_class = VerifyCodeSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return CustomResponse.error(
                request=request,
                errors=str(serializer.errors),
                message_key="CODE_VERIFICATION_ERROR"
            )
    
        user = serializer.validated_data["user"]
        tokens = user.get_tokens()
        data = {
            "user": UserSerializer(user).data,
            "tokens": tokens
        }
        
        return CustomResponse.success(
            request=request,
            data=data,
            message_key="CODE_VERIFICATED_SUCCESSFULLY"
        )

class ResendVerificationCodeAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_classes = [ResendVerificationCodeSerializer]
    
class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_classes = [LoginSerializer]
class SetPasswordAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_classes = [SetPasswordSerializer]

class UpdatePasswordAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_classes = [UpdatePasswordSerializer]
class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_classes = [MeSerializer]
    
class UpdatePhoneAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_classes = [UpdatePhoneSerializer]
class VerifyUpdateCodeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_classes = [VerifyUpdateCodeSerializer]
class ProfileUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_classes = [ProfileUpdateSerializer]
    