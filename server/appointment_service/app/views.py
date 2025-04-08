from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response

from .serializers import FetchAppointmentSeriaizer, AppointmentStatusSerializer,CreateAppointmentSeriaizer
from .permissions import IsDoctor, IsPatient, IsOwnerOrDoctor,IsPatientOrDoctor
from .models import Appointment

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
    permission_classes=[IsPatient]

    def get_queryset(self):
        return Appointment.objects.filter(patient_id=self.request.user.id)

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
