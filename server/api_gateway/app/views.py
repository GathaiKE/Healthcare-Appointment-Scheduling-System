from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from .serializers import DoctorDataSerializer, AdminSerializer, PatientSerializer
from .permissions import IsSuperAdmin
from .utilities import UserRoles


class PatientViewset(viewsets.ViewSet):
    permission_classes=[AllowAny]
    throttle_classes=[AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        request.data.update({'role',UserRoles.PATIENT})
        serializer=PatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.validated_data)
        return Response({"detail":f"Registration for patient {serializer.data.get('email')} in progress"}, status=status.HTTP_202_ACCEPTED)

class DoctorViewset(viewsets.ViewSet):
    permission_classes=[AllowAny]
    throttle_classes=[AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        request.data['role']=UserRoles.DOCTOR
        serializer=DoctorDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create_user(serializer.data)
        return Response({"detail":"Registration in progress", "data":serializer.data}, status=status.HTTP_202_ACCEPTED)


class AdministratorViewSet(viewsets.ViewSet):
    permission_classes=[IsAuthenticated, IsAdminUser]
    throttle_classes=[UserRateThrottle]

    def create(self, request, *args, **kwargs):
        request.data['role']=UserRoles.STAFF
        serializer=AdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create_user(serializer.data)
        return Response({"detail":"Registration in progress", "data":serializer.data}, status=status.HTTP_202_ACCEPTED)
    
    def make_admin(self, reuest, *args, **kwargs):
        pass

    def make_superuser(self, request, *args, **kwargs):
        pass
  