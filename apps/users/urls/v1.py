from django.urls import path

from apps.users.views.devices import UserDeviceListCreateAPIView, UserDeviceDestroyAPIView
from apps.users.views.register import LoginAPIView, MeAPIView, ProfileAPIView, RegisterAPIView, ResendVerificationCodeAPIView, SetPasswordAPIView, UpdatePasswordAPIView, UpdatePhoneAPIView, VerifyCodeAPIView, VerifyUpdateCodeAPIView

app_name = 'users'

urlpatterns = [
    # check if phone number exists, send code and give tokens
    path('register/', RegisterAPIView.as_view(), name='register'),
    # login with username/phone_number and password
    path('login/', LoginAPIView.as_view(), name='login'),
    # body: { "phone_number": "1234567890", "code": "123456" }
    path('verify/', VerifyCodeAPIView.as_view(), name='verify'),
    # body: { "phone_number": "1234567890" }
    path('resend-code/', ResendVerificationCodeAPIView.as_view(), name='resend-code'),
    # body: { "phone_number": "1234567890", "password1": "newpassword123", "password2": "newpassword123" }
    path('set-password/', SetPasswordAPIView.as_view(), name='set-password'),
    # body: { "old_password": "oldpassword123", "new_password1": "newpassword123", "new_password2": "newpassword123" }
    path('update-password/', UpdatePasswordAPIView.as_view(), name='update-password'),
    # token on the header and return user data
    path('me/', MeAPIView.as_view(), name='me'),
    # update phone number, body: { "phone_number": "1234567890"}
    path('update-phone/', UpdatePhoneAPIView.as_view(), name='update-phone'),
    # verify code and updated phone number body: { "phone_number": "1234567890", "code": "123456" }
    path('verify-update-code/', VerifyUpdateCodeAPIView.as_view(), name='verify-update-code'),
    # patch endpoint to update user data
    path('', ProfileAPIView.as_view(), name='profile'),

    # User devices management urls
    # create device and list of all user devices
    path('devices/', UserDeviceListCreateAPIView.as_view(), name='list-create-devices'),
    path('devices/<str:device_id>/', UserDeviceDestroyAPIView.as_view(), name='delete-device'),
]