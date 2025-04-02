from django.db import models
import uuid

class Appointment(models.Model):
    class Status(models.IntegerChoices):
        PENDING=0, 'pending'
        CONFIRMED=1, 'confirmed'
        CANCELLED=2, 'cancelled'
        CURRENT=3, 'current'
        DONE=4, 'done'

    id=models.UUIDField(primary_key=True,unique=True, editable=False, default=uuid.uuid4)
    doctor_id=models.CharField(max_length=100, blank=False)
    patient_id=models.CharField(max_length=100, blank=False)
    hospital_id=models.CharField(max_length=100, blank=True)
    start_time=models.DateTimeField(blank=False)
    end_time=models.DateTimeField(blank=False)
    status=models.IntegerField(choices=Status.choices, default=Status.PENDING)
    created_at=models.DateTimeField(blank=False, auto_now_add=True)
    updated_at=models.DateTimeField(blank=True)
    deleted_at=models.DateTimeField(blank=True)

    def __str__(self):
        return f"Appointment {self.id} - Status: {self.get_status_display()}"
    

    