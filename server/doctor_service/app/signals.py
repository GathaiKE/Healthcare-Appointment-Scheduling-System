# from celery import Celery
# from django.conf import settings

# app=Celery('doctor_service', broker=settings.CELERY_BROKER_URL)
# from celery import current_app as app
from doctor_service.celery import app
def create_schedue(doctor_id, **kwargs):
    app.send_task('create_doctor_calendar', args=[doctor_id], kwargs={**kwargs}, queue='appointments')

def unlink_records(doctor_id):
    app.send_task("unlink_doctor", args=[doctor_id], queue='medical_records')