from django.shortcuts import render
from rest_framework import generics, status
from django.contrib.auth import get_user_model
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import DoctorSerializer, AuthSerializer,SpecializationSerializer
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
    
class AddSpecialization(generics.ListCreateAPIView):
    queryset=Specialization.objects.all()
    serializer_class=SpecializationSerializer
    permission_classes=[AllowAny]
    throttle_classes=[UserRateThrottle]
