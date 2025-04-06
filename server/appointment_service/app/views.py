from django.shortcuts import render
from rest_framework import generics
from rest_framework.throttling import UserRateThrottle

from .serializers import AppointmentSeriaizer
from .permissions import IsPatientDoctor

# Create your views here.
# check availability of the slot
# reject unavailable slot
# book slot
class CreateAppointmentView(generics.CreateAPIView):
    serializer_class=AppointmentSeriaizer
    permission_classes=[IsPatientDoctor]
    throttle_classes=[UserRateThrottle]
# cancel reservation/slot
# create reservation with slot
# cancel reservation with slot
# fetch all reservations
# reccommend next soonest available slot.