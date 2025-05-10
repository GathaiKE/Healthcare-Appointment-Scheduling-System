from doctor_service.celery import app
from celery import shared_task
from rest_framework.response import Response
import logging

from .serializers import DoctorManageSerializer

logger=logging.getLogger(__name__)

@shared_task(name="register_doctor")
def register_doctor(message):
    action=message.get('action')
    data=message.get('data')

    if action == 'register_doctor':
        serializer=DoctorManageSerializer(data=data)

        if not serializer.is_valid():
            logger.error(f"Error occured: {serializer.errors}")
        elif serializer.is_valid():
            serializer.save()
            logger.info(f"Doctor registration successful")
        else:
            logger.error(f"Error occured: {serializer.errors}")

