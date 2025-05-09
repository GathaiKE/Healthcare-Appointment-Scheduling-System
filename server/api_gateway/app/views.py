from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from .serializers import DoctorDataSerializer
from .producer import register_doctor

class RegisterDoctorView(generics.CreateAPIView):
    serializer_class=DoctorDataSerializer
    permission_classes=[AllowAny]
    throttle_classes=[AnonRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        register_doctor(serializer.validated_data)
        
        return Response({"detail":"Registration in progress"}, status=status.HTTP_202_ACCEPTED)