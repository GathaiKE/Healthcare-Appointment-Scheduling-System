from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from celery import Celery

from .models import Patient

app=Celery('patient_service', broker='amqp://admin:admin@localhost:5672/tiberbuhost')

# @receiver(post_save, sender=Patient)
# def deactivate_patient_handler(sender, instance, **kwargs):
#     if not instance.is_active:
#         app.send_task('appointment_service.tasks.cancel_patients_appointments', args=[instance.id])

@receiver(pre_delete, sender=Patient)
def delete_patient_handler(sender, instance, **kwargs):
    app.send_task('appointment_service.tasks.cancel_patients_appointments', args=[instance.id])
