from django.urls import path

from apps.users.views.devices import UserDeviceListCreateAPIView, UserDeviceDestroyAPIView
from apps.users.views.register import RegisterAPIView

app_name = 'users'

urlpatterns = [
    # check if phone number exists, send code and give tokens
    path('register/', RegisterAPIView.as_view(), name='register'),
    # login with username/phone_number and password
    path('login/', RegisterAPIView.as_view(), name='register'),
    # body: { "phone_number": "1234567890", "code": "123456" }
    path('verify/', RegisterAPIView.as_view(), name='register'),
    # body: { "phone_number": "1234567890" }
    path('resend-code/', RegisterAPIView.as_view(), name='register'),
    # body: { "phone_number": "1234567890", "password1": "newpassword123", "password2": "newpassword123" }
    path('set-password/', RegisterAPIView.as_view(), name='register'),
    # body: { "old_password": "oldpassword123", "new_password1": "newpassword123", "new_password2": "newpassword123" }
    path('update-password/', RegisterAPIView.as_view(), name='register'),
    # token on the header and return user data
    path('me/', RegisterAPIView.as_view(), name='register'),
    # update phone number, body: { "phone_number": "1234567890"}
    path('update-phone', RegisterAPIView.as_view(), name='register'),
    # verify code and updated phone number body: { "phone_number": "1234567890", "code": "123456" }
    path('verify-update-code/', RegisterAPIView.as_view(), name='register'),
    # patch endpoint to update user data
    path('', RegisterAPIView.as_view(), name='register'),

    # User devices management urls
    # create device and list of all user devices
    path('devices/', UserDeviceListCreateAPIView.as_view(), name='list-create-devices'),
    path('devices/<str:device_id>/', UserDeviceDestroyAPIView.as_view(), name='delete-device'),
]