from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.throttling import AnonRateThrottle,UserRateThrottle

from .serializers import RecordSerializer, TestSerializer
from .models import MedicalRecord, Test, RecordOwnership
from .permissions import IsOwnerOrDoctor, IsDoctor


class ListDoctorRecords(generics.ListAPIView):
    serializer_class=RecordSerializer
    permission_classes=[IsDoctor]
    throttle_classes=[UserRateThrottle]

    def get_queryset(self):
        doctor_id = self.request.user.id
        return RecordOwnership.objects.filter(record_ownership__doctor_id=doctor_id)

# create record
class CreateRecordView(generics.CreateAPIView):
    serializer_class=RecordSerializer
    permission_classes=[IsDoctor]
    throttle_classes=[UserRateThrottle]

# update record
class RecordUpdateView(generics.UpdateAPIView):
    queryset=MedicalRecord.objects.all()
    serializer_class=RecordSerializer
    permission_classes=[IsDoctor]
    throttle_classes=[UserRateThrottle]

# fetch record
class RecordRetrieveView(generics.RetrieveAPIView):
    queryset=MedicalRecord.objects.all()
    serializer_class=RecordSerializer
    permission_classes=[IsOwnerOrDoctor]
    throttle_classes=[UserRateThrottle]

# delete record
class RecordDestroyView(generics.DestroyAPIView):
    queryset=MedicalRecord.objects.all()
    serializer_class=RecordSerializer
    permission_classes=[IsDoctor]
    throttle_classes=[UserRateThrottle]

# update, fetch and delete test
class TestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Test.objects.all()
    serializer_class=TestSerializer
    permission_classes=[IsDoctor]
    throttle_classes=[UserRateThrottle]

