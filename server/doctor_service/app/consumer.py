from doctor_service.celery import app
from celery import shared_task
from rest_framework.response import Response
# from rest_framework import status

from .serializers import DoctorManageSerializer

@shared_task(name="doctors.process")
def register_doctor(message):
    action=message.get('action')
    data=message.get('data')

    if action == 'register_doctor':
        serializer=DoctorManageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            print(f"Doctor registration successful")
        print(f"Registration failed: {serializer.errors}")


