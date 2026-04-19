from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import serializers
from rest_framework.generics import ListAPIView

from apps.shared.utils.custom_response import CustomResponse
from apps.users.models.users import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number']


@method_decorator(cache_page(60 * 15), name='dispatch')  # Cache the response for 15 minutes
class AllUsersListAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        """List all non-deleted users"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return CustomResponse.success(
            message_key="SUCCESS",
            data=serializer.data,
            status_code=200,
            request=request
        )