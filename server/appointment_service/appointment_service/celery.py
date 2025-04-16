import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appointment_service.settings')

app=Celery('appointment_service')

app.config_from_object('django.conf:settings', namespace='CELERY')

# app.conf.task_routes={
#     'appointments.tasks.*':{'queue':'appointments'}
# }

app.autodiscover_tasks()