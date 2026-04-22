from rest_framework import status
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated

from apps.shared.utils.custom_pagination import CustomPageNumberPagination
from apps.shared.utils.custom_response import CustomResponse
from apps.users.serializers.devices import UserDeviceCreateSerializer, UserDeviceSerializer


class UserDeviceListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        return self.request.user.devices.filter(is_active=True)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserDeviceCreateSerializer
        return UserDeviceSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_data = self.get_paginated_response(serializer.data)
            return CustomResponse.success(
                message_key="DEVICE_LIST_SUCCESS",
                data=paginated_data,
                request=request
            )

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            message_key="DEVICE_LIST_SUCCESS",
            data=serializer.data,
            request=request,
            status_code=status.HTTP_200_OK
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return CustomResponse.success(
                message_key="DEVICE_CREATED",
                data=serializer.data,
                request=request,
                status_code=status.HTTP_201_CREATED
            )

        return CustomResponse.error(
            message_key="DEVICE_VALIDATION_FAILED",
            errors=serializer.errors,
            request=request,
            status_code=status.HTTP_400_BAD_REQUEST
        )


from django.shortcuts import get_object_or_404


class UserDeviceDestroyAPIView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        device_id = self.kwargs.get("pk")

        return get_object_or_404(
            self.request.user.devices,
            id=device_id,
            is_active=True
        )

    def destroy(self, request, *args, **kwargs):
        device = self.get_object()

        device.is_active = False
        device.save()

        return CustomResponse.success(
            message_key="DEVICE_DEACTIVATED",
            data={"id": device.id},
            request=request,
            status_code=status.HTTP_200_OK
        )