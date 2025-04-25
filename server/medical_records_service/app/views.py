from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.throttling import UserRateThrottle
from django.db.models import Prefetch

from .serializers import RecordSerializer, TestSerializer, RecordOwnershipSerializer,RecordUpdateSerializer
from .models import MedicalRecord, Test, RecordOwnership
from .permissions import IsOwnerOrDoctor, IsDoctor, IsPatient

# Fetch current doctor's records
class ListDoctorRecordsView(generics.ListAPIView):
    serializer_class=RecordOwnershipSerializer
    permission_classes=[IsDoctor]
    throttle_classes=[UserRateThrottle]

    def get_queryset(self):
        doctor_id = self.request.user.id
        return MedicalRecord.objects.prefetch_related(
            Prefetch(
                'recordownership_set',
                queryset=RecordOwnership.objects.filter(doctor_id=doctor_id),
                to_attr='prefetched_ownership'
            )
        ).filter(recordownership__doctor_id=doctor_id).distinct()

# Fetch current patients id
class ListPatientRecordsView(generics.ListAPIView):
    serializer_class=RecordOwnershipSerializer
    permission_classes=[IsPatient]
    throttle_classes=[UserRateThrottle]

    def get_queryset(self):
        patient_id = self.request.user.id
        return MedicalRecord.objects.prefetch_related(
            Prefetch(
                'recordownership_set',
                queryset=RecordOwnership.objects.filter(patient_id=patient_id),
                to_attr='prefetched_ownership'
            )
        ).filter(recordownership__patient_id=patient_id).distinct()

# Appointments Medical record history
class AppointmentPatientHistoryView(generics.ListAPIView):
    serializer_class=RecordOwnershipSerializer
    permission_classes=[IsOwnerOrDoctor]
    throttle_classes=[UserRateThrottle]

    def get_queryset(self):
        patiend_id=self.kwargs['patient_id']
        print(f"PATIENT ID: {patiend_id}")
        return MedicalRecord.objects.prefetch_related(
            Prefetch(
                'recordownership_set',
                queryset=RecordOwnership.objects.filter(patient_id=patiend_id),
                to_attr='prefetched_ownership'
            )
        ).filter(recordownership__patient_id=patiend_id).distinct()

# create record
class CreateRecordView(generics.CreateAPIView):
    serializer_class=RecordSerializer
    permission_classes=[IsDoctor]
    throttle_classes=[UserRateThrottle]

# update record
class RecordUpdateView(generics.UpdateAPIView):
    queryset=MedicalRecord.objects.all()
    serializer_class=RecordUpdateSerializer
    permission_classes=[IsDoctor]
    throttle_classes=[UserRateThrottle]

# fetch record
class RecordRetrieveView(generics.RetrieveAPIView):
    serializer_class=RecordOwnershipSerializer
    permission_classes=[IsOwnerOrDoctor]
    throttle_classes=[UserRateThrottle]

    def get_queryset(self):
        pk=self.kwargs['pk']
        return MedicalRecord.objects.prefetch_related(
            Prefetch(
                'recordownership_set',
                queryset=RecordOwnership.objects.filter(record_id=pk),
                to_attr='prefetched_ownership'
            )
        )

# # delete record
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

