from celery import shared_task
from datetime import timedelta

from .models import Appointment, DoctorCalender

@shared_task
def cancel_patients_appointments(patient_id):
    appointments = Appointment.objects.filter(patient_id=patient_id)
    for appointment in appointments:
        appointment.delete()
        

@shared_task(name="appointment_service.tasks.create_doctor_calender")
def create_doctor_calender(doctor_id, shift_start=None, shift_end=None, break_start=None, break_duration=None):
    DoctorCalender.objects.create(
        doctor_id=doctor_id,
        shift_start=shift_start or '09:00:00',
        shift_end=shift_end or '17:00:00',
        break_start=break_start or '13:00:00',
        break_duration=break_duration or 60
    )




