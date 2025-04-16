import os
from django.conf import settings

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctor_service.settings')

app=Celery('doctor_service')

app.config_from_object("django.conf.settings", namespace="CELERY")

app.autodiscover_tasks()
