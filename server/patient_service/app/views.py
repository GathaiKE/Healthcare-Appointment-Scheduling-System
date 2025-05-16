from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .serializers import PatientSerializer, AuthSerializer, PasswordUpdateSerializer, ListPatientSerializer,EmailCheckSerializer
from .permissions import IsOwnerOrAdmin, IsOwner

Patient=get_user_model()

class AuthenticateView(APIView):
    serialializer_class=AuthSerializer
    permission_classes=[AllowAny]
    throttle_classes=[AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer=self.serialializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        user=serializer.user

        response={
            'access': serializer.validated_data['access'],
            'refresh': serializer.validated_data['refresh'],
            'user': {
                'id': str(user.id),
                'first_name': user.first_name,
                'last_name': user.last_name,
                'surname': user.surname,
                'email': user.email,
                'phone': user.phone,
                'is_active': user.is_active,
                'date_joined': user.date_joined,
                'last_login': user.last_login
            }
        }
        return Response(response, status=status.HTTP_201_CREATED)

class PatientsListView(generics.ListAPIView):
    queryset=Patient.objects.all()
    serializer_class=ListPatientSerializer
    permission_classes=[IsAuthenticated]
    throttle_classes=[AnonRateThrottle]

class PatientSelfUpdateView(generics.UpdateAPIView):
    queryset=Patient.objects.all()
    serializer_class=PatientSerializer
    permission_classes=[IsAuthenticated, IsOwner]
    throttle_classes=[UserRateThrottle]

    def get_object(self):
        return self.request.user

    # def update(self, request, *args, **kwargs):
    #     instance=self.get_object()
    #     serializer=self.get_serializer(data=request.data)
    #     if not serializer.is_valid():
    #         return Response({"errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    #     serializer.update(validated_data=serializer.validated_data, instance=instance)
    #     return Response({"detail":"Update successful"}, status=status.HTTP_202_ACCEPTED)

class PatientDetailView(generics.RetrieveDestroyAPIView):
    queryset=Patient.objects.all()
    serializer_class=ListPatientSerializer
    permission_classes=[IsAuthenticated]
    throttle_classes=[UserRateThrottle]

class PasswordUpdateView(generics.UpdateAPIView):
    serializer_class=PasswordUpdateSerializer
    permission_classes=[IsAuthenticated]
    throttle_classes=[UserRateThrottle]

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user=self.get_object()
        serializer=self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.data.get('old_password')):
                return Response({"old_password":['wrong_password']}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get(('new_password')))
            user.save()
            return Response({"detail":"Password updated"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CurrentUserView(generics.RetrieveAPIView):
    serializer_class=ListPatientSerializer
    permission_classes=[IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class PatientActiveStatusView(generics.RetrieveUpdateAPIView):
    queryset=Patient.objects.all()
    serializer_class=PatientSerializer
    permission_classes=[IsAdminUser]
    throttle_classes=[AnonRateThrottle]
    lookup_field='pk'

    def update(self,request, *args, **kwargs):
        patient=self.get_object()

        if patient == request.user and not request.data.get('is_staff', True):
            return Response({"detail":"Cannot change your own status"}, status=status.HTTP_403_FORBIDDEN)
        serializer=self.get_serializer(data=request.data)
        new_status=request.data.get('is_active')

        if serializer.is_valid():
            if patient.is_active != new_status:
                patient.is_active=new_status
                patient.save()
                return Response({"detail":f"{patient.first_name} os not {"active" if patient.is_active else "inactive"}"}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"detail":f"{patient.fist_name} {patient.last_name} is aready {"active" if patient.is_active else "inactive"}"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# Email validity view
class CheckEmailView(generics.GenericAPIView):
    serializer=EmailCheckSerializer
    permission_classes=[AllowAny]
    throttle_classes=[UserRateThrottle]

    def get(self, request, *args, **kwargs):
        email=request.query_params.get('email')
        if not email:
            return Response({"error":"Email parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        serializer=self.serializer(data={'email':email})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)