from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import FetchAppointmentSeriaizer, AppointmentStatusSerializer,CreateAppointmentSeriaizer, OffCalenderSerializer, UpdateAppointmentSeriaizer
from .permissions import IsDoctor, IsPatient, IsOwnerOrDoctor,IsPatientOrDoctor
from .models import Appointment, OffPeriod

class CreateAppointmentView(generics.CreateAPIView):
    queryset=Appointment.objects.all()
    serializer_class=CreateAppointmentSeriaizer
    permission_classes=[IsPatientOrDoctor]
    throttle_classes=[UserRateThrottle]

class RetrieveAppointmentView(generics.RetrieveAPIView):
    queryset=Appointment.objects.all()
    serializer_class=FetchAppointmentSeriaizer
    permission_classes=[IsOwnerOrDoctor]
    throttle_classes=[UserRateThrottle]
    lookup_field='pk'

class RescheduleAppointmentView(generics.UpdateAPIView):
    queryset=Appointment.objects.all()
    serializer_class=UpdateAppointmentSeriaizer
    permission_classes=[IsDoctor]
    throttle_classes=[UserRateThrottle]

class CancelAppointmentView(generics.UpdateAPIView):
    serializer_class=AppointmentStatusSerializer
    permission_classes=[IsDoctor]
    throttle_classes=[UserRateThrottle]

    def update(self, request, pk=None, *args, **kwargs):
        try:
            appointment=Appointment.objects.get(id=pk)
            appointment.delete()
            return Response({"detail":f"Appointment has been cancelled"})
        except Appointment.DoesNotExist:
            return Response({"detail":"Appointment was not found"}, status=status.HTTP_404_NOT_FOUND)
      
class PatientAppointmentsView(generics.ListAPIView):
    serializer_class=FetchAppointmentSeriaizer
    permission_classes=[IsAuthenticated, IsPatient]
    throttle_classes=[UserRateThrottle]

    def get_queryset(self):
        result=Appointment.objects.filter(patient_id=self.request.user.id)
        return result

class DoctorAppointmentsView(generics.ListAPIView):
    serializer_class=FetchAppointmentSeriaizer
    permission_classes=[IsDoctor]

    def get_queryset(self):
        return Appointment.objects.filter(slot__doctor_id=self.request.user.id).select_related('slot')

class AppointmentStatusView(generics.UpdateAPIView):
    serializer_class=AppointmentStatusSerializer
    permission_classes=[IsDoctor]
    throttle_classes=[UserRateThrottle]

    def update(self, request, pk=None, *args, **kwargs):
        serializer=self.serializer_class(data=request.data)

        if serializer.is_valid():
            try:
                appointment=Appointment.objects.get(id=pk)
                new_status=serializer.data.get('status')
                if new_status not in [0,1,2,3]:
                    return Response({"detail":"Invalid status code provided"}, status=status.HTTP_400_BAD_REQUEST)
                if appointment.status == new_status:
                    return Response({"detail":f"This appointment is already {appointment.status}"}, status=status.HTTP_400_BAD_REQUEST)
                appointment.status=new_status
                appointment.save()
                return Response({"detail":f"Appointment is now {appointment.status}"})
            except Appointment.DoesNotExist:
                return Response({"detail":"Appointment was not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# create off period entry
class CreateOffCalenderView(generics.CreateAPIView):
    serializer_class=OffCalenderSerializer
    permission_classes=[IsDoctor, IsAuthenticated]
    throttle_classes=[UserRateThrottle]

# Fetch doctors off calender days
class FetchOffCalenderView(generics.ListAPIView):
    serializer_class=OffCalenderSerializer
    permission_classes=[IsAuthenticated]
    throttle_classes=[UserRateThrottle]

    def get_queryset(self, pk=None):
        return OffPeriod.objects.filter(doctor_id=pk)

# Update off entry details
class OffCalenderUpdateView(generics.UpdateAPIView):
    queryset=OffPeriod.objects.all()
    serializer_class=OffCalenderSerializer
    permission_classes=[IsAuthenticated, IsDoctor]
    throttle_classes=[UserRateThrottle]
    lookup_field='pk'

# Delete Off calender entry
class OffCalenderDestroyView(generics.DestroyAPIView):
    queryset=OffPeriod.objects.all()
    serializer_class=OffCalenderSerializer
    permission_classes=[IsAuthenticated, IsDoctor]
    throttle_classes=[UserRateThrottle]
    lookup_field='pk'

# Fetch Off calender days
class OffCalenderRetrieveView(generics.RetrieveAPIView):
    queryset=OffPeriod.objects.all()
    serializer_class=OffCalenderSerializer
    permission_classes=[IsAuthenticated]
    throttle_classes=[UserRateThrottle]
    lookup_field='pk'

# task to send email once the appointment is created or changed or deleted.
# Notification sservice to send notifications to the front end client once the appointment is created.
