from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response


from .serializers import AppointmentSeriaizer, AppointmentStatusSerializer
from .permissions import IsPatientDoctor, IsDoctor, IsPatient
from .models import Appointment

# Create your views here.
# check availability of the slot
# reject unavailable slot
# book slot
# cancel reservation/slot
# create reservation with slot
class CreateAppointmentView(generics.ListCreateAPIView):
    queryset=Appointment.objects.all()
    serializer_class=AppointmentSeriaizer
    permission_classes=[IsPatientDoctor]
    throttle_classes=[UserRateThrottle]
    
# cancel reservation with slot
class CancelAppointmentView(generics.UpdateAPIView):
    serializer_class=AppointmentStatusSerializer
    permission_classes=[IsDoctor]
    throttle_classes=[UserRateThrottle]

    def update(self, request, pk=None, *args, **kwargs):
        serializer=self.serializer_class(data=request.data)

        if serializer.is_valid():
            try:
                appointment=Appointment.objects.get(id=pk)
                new_status=2
                appointment.status=new_status
                appointment.save()
                return Response({"detail":f"Appointment has been cancelled"})
            except Appointment.DoesNotExist:
                return Response({"detail":"Appointment was not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientAppointments(generics.ListAPIView):
    serializer_class=AppointmentSeriaizer
    permission_classes=[IsPatient]

    def get_queryset(self):
        return Appointment.objects.filter(patient_id=self.request.user.id)


class DoctorAppointments(generics.ListAPIView):
    serializer_class=AppointmentSeriaizer
    permission_classes=[IsDoctor]

    def get_queryset(self):
        return Appointment.objects.filter(slot__doctor_id=self.request.user.id).select_related('slot')

# Update the appointment status
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
                if new_status not in [0,1,3,4]:
                    return Response({"detail":"Invalid status code provided"}, status=status.HTTP_400_BAD_REQUEST)
                if appointment.status == 2:
                    return Response({"detail":"This appointment has already been cancelled"}, status=status.HTTP_400_BAD_REQUEST)
                appointment.status=new_status
                appointment.save()
                return Response({"detail":f"Appointment is now {appointment.status}"})
            except Appointment.DoesNotExist:
                return Response({"detail":"Appointment was not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# fetch all reservations
# reccommend next soonest available slot.