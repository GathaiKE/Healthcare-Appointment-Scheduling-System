from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle

from .serializers import PatientSerializer

class CreatePatientView(generics.CreateAPIView):
    serializer_class=PatientSerializer
    permission_classes=[AllowAny]
    throttle_classes=[AnonRateThrottle]

