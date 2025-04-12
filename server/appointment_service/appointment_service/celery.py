import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointment_service.settings')

app=Celery('appointment_service', broker='amqp://admin:admin@localhost:5672/tiberbuhost')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(['appointment_service'])