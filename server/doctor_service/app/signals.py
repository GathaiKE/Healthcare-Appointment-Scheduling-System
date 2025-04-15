from celery import Celery
from django.conf import settings

app=Celery('doctor_service', broker=settings.CELERY_BROKER_URL)

def create_schedue(doctor_id, **kwargs):
    app.send_task('appointment_service.tasks.create_doctor_calender', args=[doctor_id], kwargs={**kwargs})