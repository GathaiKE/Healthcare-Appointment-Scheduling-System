from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status, generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from .serializers import DoctorDataSerializer, AdminSerializer, PatientSerializer, AuthenticationDataSerializer,PasswordChangeSerializer, PasswordResetSerializer
from .permissions import IsSuperAdmin
from .utilities import UserRoles, DataFetcher, UserDataManager, Authenticator


class AuthenticationViewSet(viewsets.ViewSet):
    permission_classes=[AllowAny]
    throttle_classes=[AnonRateThrottle]

    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer=AuthenticationDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        authenticator=Authenticator(request_headers=request.headers)
        result, error=authenticator.patient_login(serializer.validated_data)

        if error:
            return Response(
                {
                    'error': error['error'],
                    'detail': error['detail'],
                    **error.get('original_response', {})
                },
                status=error.get('status', status.HTTP_500_INTERNAL_SERVER_ERROR)
            )
            
        return Response(
            result['data'], 
            status=result.get('status', status.HTTP_200_OK)
        )
    
    @action(detail=False, methods=["get"])
    def me(self, request):
        authenticator=Authenticator(request=request)
        result, error = authenticator.current_user()

        if error and result is None:
            return Response({"detail":f"{error.get('error')}: {error.get('detail')}", 'original_error': error.get('original_error', '')}, status=error.get('status'))
        return Response(result["data"], status=result.get('status', status.HTTP_200_OK))

    @action(detail=False, methods=['put'])
    def changepassword(self, request):
        serializer=PasswordChangeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        manager=UserDataManager(request=request)
        result, error=manager.change_password(validated_data=serializer.validated_data)

        if result is None and error:
            return Response({"detail":f"{error['error']}:{error['detail']}"}, status=error.get('status', status.HTTP_400_BAD_REQUEST))
        return Response({"detail": result['detail'], "data":result['data']}, status=result.get('status', status.HTTP_200_OK))



class PatientViewSet(viewsets.ViewSet):
    permission_classes=[AllowAny]
    throttle_classes=[AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer=PatientSerializer(data=request.data, context={'request':request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.create(serializer.validated_data)
        return Response({"detail":f"Registration for patient {serializer.data.get('email')} in progress"}, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=["put"])
    def selfupdate(self, request, *args, **kwargs):
        serializer=PatientSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        manager=UserDataManager(request=request)
        result, error=manager.update_self_data(validated_data=serializer.validated_data)
        if result is None and error:
            return Response({"detail":f"{error['error']}:{error['detail']}"}, status=error.get('status',status.HTTP_400_BAD_REQUEST))
        return Response({'detail': result['detail'],'data':result['data']}, status=result.get('status', status.HTTP_202_ACCEPTED))
    
    def retrieve(self, request, pk=None):
        fetcher=DataFetcher(request=request)
        response, error=fetcher.fetch_patient_detail(pk)
        if  error and response is None:
            return Response({"detail":f"{error.get('error')}: {error.get('detail')}"}, status=error.get('status'))
        return Response(response['data'], status=response.get('status', status.HTTP_200_OK))
      
    def list(self, request):
        fetcher=DataFetcher(request=request)
        response, error=fetcher.fetch_patients()
        if error and response is None:
            return Response({"detail":f"Error: {error.get('detail')}"}, status=error.get('status'))
        return Response(response['data'], status=response.get('status', status.HTTP_200_OK))
    
    def destroy(self, request, pk=None):
        manager=UserDataManager(request=request)
        response, err=manager.delete_patient(pk)
        if err and response is None:
            return Response({"detail":f"{err['error']}:{err['detail']}"}, status=err['status'])
        return Response({"detail":response['detail']}, status=response['status'])

    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer=AuthenticationDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        authenticator=Authenticator(request=request)
        result, error=authenticator.patient_login(serializer.validated_data)

        if error:
            return Response(
                {
                    'error': error['error'],
                    'detail': error['detail'],
                    **error.get('original_response', {})
                },
                status=error.get('status', status.HTTP_500_INTERNAL_SERVER_ERROR)
            )
            
        return Response(
            result['data'], 
            status=result.get('status', status.HTTP_200_OK)
        )

    @action(detail=True, methods=['put'])
    def resetpassword(self, request, pk=None):
        serializer=PasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        manager=UserDataManager(request=request)
        result, error=manager.reset_password(validated_data=serializer.validated_data,role=UserRoles.PATIENT,  pk=pk)

        if result is None and error:
            return Response({"detail":f"{error['error']}:{error['detail']}"}, status=error.get('status', status.HTTP_400_BAD_REQUEST))
        return Response({"detail": result['detail'], "data":result['data']}, status=result.get('status', status.HTTP_200_OK))

    
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
  