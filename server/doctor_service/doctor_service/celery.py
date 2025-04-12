import os
from django.conf import settings

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctor_service.settings')

app=Celery('doctor_service', broker=settings.CELERY_BROKER_URL)

app.config_from_object("django.conf.settings", namespace="CELERY")

app.autodiscover_tasks(['doctor_service'])
