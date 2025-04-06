from django.shortcuts import render
from rest_framework import generics, status
from django.contrib.auth import get_user_model
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import DoctorSerializer, AuthSerializer,SpecializationSeriaizer, PasswordUpdateSerializer, PasswordResetSerializer
from .models import Specialization

Doctor=get_user_model()

class RegisterDoctorView(generics.CreateAPIView):
    serializer_class=DoctorSerializer
    permission_classes=[AllowAny]
    throttle_classes=[AnonRateThrottle]

class LogInView(APIView):
    serializer_class=AuthSerializer
    permission_classes=[AllowAny]
    throttle_classes=[AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer=self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        doctor=serializer.user
        return Response({
            'access': serializer.validated_data['access'],
            'refresh': serializer.validated_data['refresh'],
            'user': {
                'id': str(doctor.id),
                'surname': doctor.surname,
                'first_name': doctor.first_name,
                'last_name': doctor.last_name,
                'email': doctor.email,
                'phone': doctor.phone,
                'specialization': str(doctor.specialization),
                'id_number': doctor.id_number,
                'is_active': doctor.is_active,
                'date_joined': doctor.date_joined,
                'updated_at': doctor.updated_at,
                'deleted_at': doctor.deleted_at
            }
        }, status=status.HTTP_202_ACCEPTED)
    
class SpecializationView(generics.ListCreateAPIView):
    queryset=Specialization.objects.all()
    serializer_class=SpecializationSeriaizer
    permission_classes=[IsAuthenticated]
    throttle_classes=[UserRateThrottle]

# List all doctors
class DoctorsListView(generics.ListAPIView):
    queryset=Doctor.objects.all()
    serializer_class=DoctorSerializer
    permission_classes=[IsAuthenticated]
    throttle_classes=[UserRateThrottle]
    
# Retrieve, update and Delete a doc
class DoctorDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Doctor.objects.all()
    serializer_class=DoctorSerializer
    permission_classes=[IsAuthenticated]
    throttle_classes=[UserRateThrottle]

# Update password
class DoctorPasswordUpdateView(generics.UpdateAPIView):
    serializer_class=PasswordUpdateSerializer
    permission_classes=[IsAuthenticated]
    throttle_classes=[UserRateThrottle]

    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        serializer=self.serializer_class(data=request.data)
        doctor=self.get_object()
        
        if serializer.is_valid():
            if not doctor.check_password(serializer.data.get('old_password')):
                return Response({"old_password":["Wrong password"]}, status=status.HTTP_400_BAD_REQUEST)
            doctor.set_password(serializer.data.get('new_password'))
            doctor.save()
            return Response({"detail":"Password update successfull"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# Reset password
class ResetPasswordView(APIView):
    permission_classes=[AllowAny]
    throttle_classes=[AnonRateThrottle]

    def post(self, request, pk=None):
        serializer=PasswordResetSerializer(data=request.data)

        if serializer.is_valid():
            new_password=serializer.data.get('new_password')

            try:
                doctor=Doctor.objects.get(id=pk)
                doctor.set_password(new_password)
                doctor.save()
                return Response({"detail":"Your password was reset successfully"}, status=status.HTTP_202_ACCEPTED)
            except Doctor.DoesNotExist:
                return Response({"detail":"Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# get current active user
class CurrentUserView(generics.RetrieveAPIView):
    serializer_class=DoctorSerializer
    permission_classes=[IsAuthenticated]

    def get_object(self):
        print(" current user is: ",self.request.user)
        return self.request.user
        
# get doctors visits and patients
# Access a patients information using their ref id
