from celery import shared_task
import logging

from .serializers import LicenseSerializer

logger=logging.getLogger(__name__)

@shared_task(name="create_license_entry")
def create_license_entry(message):
    action=message.get("action")
    data=message.get("data")

    serializer=LicenseSerializer(data=data)
    if action=='create_license_entry':
        if not serializer.is_valid:
            logger.error(f"Invalid data:{serializer.errors}")
        serializer.save()
        logger.info(f"License entry created: {serializer.data}")

