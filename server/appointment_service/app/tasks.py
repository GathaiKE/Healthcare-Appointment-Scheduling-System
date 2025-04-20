from celery import shared_task
from datetime import timedelta

from .models import Appointment, DoctorCalender

# @shared_task(name="appointment_service.tasks.cancel_patient_appointments")
@shared_task(name="cancel_patient_appointments")
def cancel_patients_appointments(patient_id):
    appointments = Appointment.objects.filter(patient_id=patient_id)
    for appointment in appointments:
        appointment.delete()
        
        
@shared_task(name="cancel_doctor_appointments")
def cancel_doctors_appointments(doctor_id):
    appointments = Appointment.objects.filter(doctor_id=doctor_id)
    for appointment in appointments:
        appointment.delete()


@shared_task(name="create_doctor_calendar")
def create_doctor_calender(doctor_id, shift_start=None, shift_end=None, break_start=None, break_duration=None):
    DoctorCalender.objects.create(
        doctor_id=doctor_id,
        weekday_shift_start=shift_start or '09:00:00',
        weekday_shift_end=shift_end or '17:00:00',
        weekday_break_start=break_start or '13:00:00',
        weekday_break_duration=break_duration or 60,
        weekend_shift_start='10:00:00',
        weekend_shift_end='15:00:00',
        weekend_break_start='12:00:00',
        weekend_break_duration=40
    )

@shared_task(name="delete_doctor_calendar")
def delete_doctor_calender(doctor_id):
    calender=DoctorCalender.objects.filter(doctor_id=doctor_id)

    for item in calender:
        item.delete()
        



