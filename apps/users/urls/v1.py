from django.urls import path

from apps.users.views.register import RegisterAPIView
from apps.users.views.users import AllUsersListAPIView

app_name = 'users'

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('users/', AllUsersListAPIView.as_view(), name='users-list'),
]