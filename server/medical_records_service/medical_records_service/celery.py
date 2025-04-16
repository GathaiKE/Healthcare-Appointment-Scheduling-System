import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medical_records_service.settings")

app=Celery("medical_records")

app.config_from_object('django.conf:settings', namespace="CELERY")

# app.conf.task_routes={
#     'medical_records.*':{'queue':'medical_records'}
# }

app.autodiscover_tasks()