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
    

class Appointment(models.Model):
    class Status(models.IntegerChoices):
        PENDING=0, 'pending'
        CONFIRMED=1, 'confirmed'
        CANCELLED=2, 'cancelled'
        MISSED=3, 'missed'
        DONE=4, 'done'
    id=models.UUIDField(primary_key=True,unique=True, editable=False, default=uuid.uuid4)
    patient_id=models.CharField(max_length=100, blank=False)
    hospital_id=models.CharField(max_length=100, blank=True)
    slot=models.ForeignKey(Slot, on_delete=models.CASCADE)
    status=models.IntegerField(choices=Status.choices, default=Status.PENDING)
    created_at=models.DateTimeField(blank=False, auto_now_add=True)
    updated_at=models.DateTimeField(blank=True, null=True)
    deleted_at=models.DateTimeField(blank=True, null=True)

    # def __str__(self):
    #     return f"Appointment {self.id} - Status: {self.get_status_display()}"


class DoctorCalender(models.Model):
    pass