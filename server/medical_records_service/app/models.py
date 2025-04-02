from django.db import models
import uuid

class Visit(models.Model):
    id=models.UUIDField(primary_key=True,unique=True, editable=False, default=uuid.uuid4)
    doctor_id=models.CharField(blank=False)
    patient_id=models.CharField(blank=False)
    hospital_id=models.CharField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True, blank=False)
    updated_at=models.DateTimeField(blank=True)
    deleted_at=models.DateTimeField(blank=True)

class VisitFindings(models.Model):
    id=models.UUIDField(primary_key=True,unique=True)
