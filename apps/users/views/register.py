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
    serializer_class = ResendVerificationCodeSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return CustomResponse.error(
                request=request,
                errors=str(serializer.errors),
                message_key="RESEND_CODE_ERROR"
            )

        user = serializer.validated_data["user"]

        send_verification_code.delay(user.id)

        return CustomResponse.success(
            request=request,
            message_key="CODE_SENT_SUCCESSFULLY"
        )
    
class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return CustomResponse.error(
                request=request,
                errors=str(serializer.errors),
                message_key="LOGIN_ERROR"
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
            message_key="LOGIN_SUCCESS"
        )
class SetPasswordAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = SetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return CustomResponse.error(
                request=request,
                errors=str(serializer.errors),
                message_key="SET_PASSWORD_ERROR"
            )

        user = serializer.save()

        return CustomResponse.success(
            request=request,
            message_key="PASSWORD_SET_SUCCESSFULLY"
        )

class UpdatePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdatePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )

        if not serializer.is_valid():
            return CustomResponse.error(
                request=request,
                errors=str(serializer.errors),
                message_key="UPDATE_PASSWORD_ERROR"
            )

        serializer.save()

        return CustomResponse.success(
            request=request,
            message_key="PASSWORD_UPDATED_SUCCESSFULLY"
        )
class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return CustomResponse.success(
            request=request,
            data=MeSerializer(request.user).data,
            message_key="USER_DATA_SUCCESS"
        )
    
class UpdatePhoneAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdatePhoneSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return CustomResponse.error(
                request=request,
                errors=str(serializer.errors),
                message_key="UPDATE_PHONE_ERROR"
            )

        phone_number = serializer.validated_data["phone_number"]

        # временно сохраняешь (или куда-то кладёшь)
        request.user.phone_number = phone_number
        request.user.save()

        send_verification_code.delay(request.user.id)

        return CustomResponse.success(
            request=request,
            message_key="PHONE_UPDATE_CODE_SENT"
        )
        
class VerifyUpdateCodeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = VerifyUpdateCodeSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request}
        )

        if not serializer.is_valid():
            return CustomResponse.error(
                request=request,
                errors=str(serializer.errors),
                message_key="VERIFY_UPDATE_CODE_ERROR"
            )

        return CustomResponse.success(
            request=request,
            message_key="PHONE_UPDATED_SUCCESSFULLY"
        )
        
class ProfileUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileUpdateSerializer

    def patch(self, request):
        serializer = self.serializer_class(
            request.user,
            data=request.data,
            partial=True
        )

        if not serializer.is_valid():
            return CustomResponse.error(
                request=request,
                errors=str(serializer.errors),
                message_key="PROFILE_UPDATE_ERROR"
            )

        serializer.save()

        return CustomResponse.success(
            request=request,
            data=UserSerializer(request.user).data,
            message_key="PROFILE_UPDATED_SUCCESSFULLY"
        )
    