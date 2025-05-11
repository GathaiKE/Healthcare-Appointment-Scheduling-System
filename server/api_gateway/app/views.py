from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from .serializers import DoctorDataSerializer, AdminSerializer, PatientSerializer, AuthenticationDataSerializer
from .permissions import IsSuperAdmin
from .utilities import UserRoles, DataFetcher, UserDataManager, Authenticator

class PatientViewSet(viewsets.ViewSet):
    permission_classes=[AllowAny]
    throttle_classes=[AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        request.data.update({'role',UserRoles.PATIENT})
        serializer=PatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create(serializer.validated_data)
        return Response({"detail":f"Registration for patient {serializer.data.get('email')} in progress"}, status=status.HTTP_202_ACCEPTED)

    def update(self, request, *args, **kwargs):
        request.data.update({'role',UserRoles.PATIENT})
        serializer=PatientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(serializer.validated_data)
        return Response({"detail":f"Update for patient {serializer.data.get('email')} in initiated"}, status=status.HTTP_202_ACCEPTED)
    
    def retrieve(self, request, pk=None):
        fetcher=DataFetcher(request_headers=request)
        instance, error=fetcher.fetch_patient_detail(pk)
        if  error:
            return error
        return instance
    
    def list(self, request):
        fetcher=DataFetcher(request_headers=request.headers)
        patients, error=fetcher.fetch_patients()
        print(f"PATIENTS RESPONSE OBJECT: ", patients)
        print(f"PATIENTS ERROR OBJECT: ", error)
        if error:
            return Response({"detail":f"Error: {error.get('detail')}"}, status=status.HTTP_401_UNAUTHORIZED)
        return patients
    
    def destroy(self, request, pk=None):
        manager=UserDataManager(request_headers=request.headers)
        response, err=manager.delete_patient(pk)
        if err:
            return err
        return response

    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer=AuthenticationDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        authenticator=Authenticator(request_headers=request.headers)
        auth_response, err=authenticator.patient_login(serializer.validated_data)

        if err:
            return Response({"detail":f"Error: {err.get('detail') if err['detail'] else err.get('error')}"}, status=status.HTTP_400_BAD_REQUEST)
        return auth_response

    
class DoctorViewSet(viewsets.ViewSet):
    permission_classes=[AllowAny]
    throttle_classes=[AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        request.data.update({'role',UserRoles.DOCTOR})
        serializer=DoctorDataSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create_user(serializer.data)
        return Response({"detail":"Registration in progress", "data":serializer.data}, status=status.HTTP_202_ACCEPTED)

class AdministratorViewSet(viewsets.ViewSet):
    permission_classes=[IsAuthenticated, IsAdminUser]
    throttle_classes=[UserRateThrottle]

    def create(self, request, *args, **kwargs):
        request.data.update({'role',UserRoles.STAFF})
        serializer=AdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create_user(serializer.data)
        return Response({"detail":"Registration in progress", "data":serializer.data}, status=status.HTTP_202_ACCEPTED)
    
    def make_admin(self, reuest, *args, **kwargs):
        pass

    def make_superuser(self, request, *args, **kwargs):
        pass
  