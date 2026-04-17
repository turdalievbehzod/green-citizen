from django.urls import path

from apps.users.views.register import RegisterAPIView

app_name = 'users'

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
]