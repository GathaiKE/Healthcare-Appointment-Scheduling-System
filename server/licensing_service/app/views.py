from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import License, User
from .serializers import LicenseSerializer, UserSerializer
from .permissions import IsAdminUser, IsDoctor


class LicenseViewSet(viewsets.ModelViewSet):
    queryset = License.objects.all()
    serializer_class = LicenseSerializer

    def get_permissions(self):
        if self.action in ['create', 'update','retrieve']:
            return [IsAuthenticated(), IsDoctor()]
        elif self.action in ['approve', 'disapprove', 'suspend', 'cancel', 'extend','list']:
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not isinstance(instance, License):
            return Response(
                {'error': 'Invalid license instance.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        allowed_fields = {'face_image', 'id_card', 'certificate'}
        data = {key: value for key, value in request.data.items() if key in allowed_fields}

        if not data:
            return Response(
                {'error': 'No valid fields provided for update.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        for field in ['face_img', 'id_card', 'practicing_certificate']:
            if field in serializer.validated_data:
                file = getattr(serializer.instance.user, field, None)
                if file:
                    file.delete()
        serializer.save(user=serializer.instance.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def extend(self, request, pk=None):
        license_instance = self.get_object()
        if license_instance.application_is_complete:
            license_instance.extend_license(days=365)
            return Response({'status': 'License extended by a year'}, status=status.HTTP_200_OK)
        return Response({'status':'This application is not complete'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        license_instance = self.get_object()
        if license_instance.application_is_complete:
            license_instance.grant_license()
            return Response({'status': 'License approved'}, status=status.HTTP_200_OK)
        return Response({'error':'Cannot approve an incomplete application'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def disapprove(self, request, pk=None):
        license_instance = self.get_object()
        license_instance.disapprove_license()
        return Response({'status': 'License disapproved'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        license_instance = self.get_object()
        license_instance.suspend_license()
        return Response({'status': 'License suspended'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        license_instance = self.get_object()
        license_instance.cancel_license()
        return Response({'status': 'License cancelled'}, status=status.HTTP_200_OK)
        


# Apply for a license -> By default, every user should have an application created on registration. Those without the processing info ie id card, certificate and face provided need to default to pending
# Update a pending license application with face(img, jpeg), id card(pdf) and practicing certificate(pdf)
# Check completeness of user license application and its validity for license
# Check a doctors license credentials and status