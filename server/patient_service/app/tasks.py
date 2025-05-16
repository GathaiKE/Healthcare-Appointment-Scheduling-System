from celery import shared_task
import logging

from .serializers import PatientSerializer

logger=logging.getLogger(__name__)


@shared_task(name='process.registration')
def register_patient(message):
    action=message.get('action')
    data=message.get('data')


    if action=='register':
        serializer=PatientSerializer(data=data)
        if not serializer.is_valid():
            logger.error(f"Error occured: {serializer.errors}")
        else:
            serializer.save()
            logger.info("Registration successful!")