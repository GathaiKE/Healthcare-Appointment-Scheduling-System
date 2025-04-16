from celery import shared_task

from .models import RecordOwnership

# @shared_task(name="medical_records_service.tasks.unlink_doctor")
@shared_task(name="unlink_doctor")
def unlink_doctor(doctor_id):
    records=RecordOwnership.objects.filter(doctor_id=doctor_id)

    for rec in records:
        rec.doctor_id=None
        rec.save()

# @shared_task(name="medical_records_service.tasks.unlink_patient")
@shared_task(name="unlink_patient")
def unlink_patient(patient_id):
    records=RecordOwnership.objects.filter(patient_id=patient_id)

    for rec in records:
        rec.doctor_id=None
        rec.save()