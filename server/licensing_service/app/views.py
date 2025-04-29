from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import License, User
from .serializers import LicenseSerializer, UserSerializer

class LicenseViewSet(viewsets.ModelViewSet):
    queryset = License.objects.all()
    serializer_class = LicenseSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        license_instance = self.get_object()
        license_instance.status = License.LicenseStatus.APPROVED
        license_instance.save()
        return Response({'status': 'License approved'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def disapprove(self, request, pk=None):
        license_instance = self.get_object()
        license_instance.status = License.LicenseStatus.DISAPPROVED
        license_instance.save()
        return Response({'status': 'License disapproved'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        license_instance = self.get_object()
        license_instance.status = License.LicenseStatus.SUSPENDED
        license_instance.save()
        return Response({'status': 'License suspended'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        license_instance = self.get_object()
        license_instance.status = License.LicenseStatus.CANCELLED
        license_instance.save()
        return Response({'status': 'License cancelled'}, status=status.HTTP_200_OK)


# Apply for a license -> By default, every user should have an application created on registration. Those without the processing info ie id card, certificate and face provided need to default to pending


# Update a pending license application with face(img, jpeg), id card(pdf) and practicing certificate(pdf)
# Check completeness of user license application and its validity for license
# Check a doctors license credentials and status
# Approve license
# Disapprove license
# Extend license
# Cancel license
# Suspend and unsuspend license