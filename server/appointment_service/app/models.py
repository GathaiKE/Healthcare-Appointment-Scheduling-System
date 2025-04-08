from django.db import models
import uuid


class Slot(models.Model):
    id=models.UUIDField(primary_key=True,unique=True, editable=False, default=uuid.uuid4)
    doctor_id=models.CharField(max_length=100, blank=False)
    date=models.DateField()
    start_time=models.TimeField()
    end_time=models.TimeField()

    def __str__(self):
        return f"Date:{self.date} From: {self.start_time} To: {self.end_time}"
    
class DoctorCalender(models.Model):
    id=models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    doctor_id=models.CharField(blank=False, unique=True)
    shift_start=models.TimeField(default='09:00:00')
    shift_end=models.TimeField(default='17:00:00')
    break_start=models.TimeField(default='13:00:00')
    break_duration=models.IntegerField(default=1)

class Appointment(models.Model):
    class Status(models.IntegerChoices):
        PENDING=0, 'pending'
        CONFIRMED=1, 'confirmed'
        DONE=2, 'done'
        MISSED=3, 'missed'
    id=models.UUIDField(primary_key=True,unique=True, editable=False, default=uuid.uuid4)
    patient_id=models.CharField(max_length=100, blank=False)
    hospital_id=models.CharField(max_length=100, blank=True)
    slot=models.ForeignKey(Slot, on_delete=models.CASCADE)
    status=models.IntegerField(choices=Status.choices, default=Status.PENDING)
    created_at=models.DateTimeField(blank=False, auto_now_add=True)
    updated_at=models.DateTimeField(blank=True, null=True)
    deleted_at=models.DateTimeField(blank=True, null=True)


