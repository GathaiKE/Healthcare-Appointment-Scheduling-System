from django.db import models
import uuid

class Test(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    name=models.CharField(max_length=100, blank=False, null=False)
    result=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(blank=True, null=True)
    deleted_at=models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class HIVStatus(models.IntegerChoices):
    NEGATIVE=0, 'negative',
    POSITIVE=1, 'positive'

class BloodGroup(models.IntegerChoices):
    A_POSITIVE=0, 'A+'
    A_NEGATIVE=1, 'A-'
    B_POSITIVE=2, 'B+'
    B_NEGATIVE=3, 'B-'
    AB_POSITIVE=4, 'AB+'
    AB_NEGATIVE=5, 'AB-'
    O_NEGATIVE=6, 'O-'
    O_POSITIVE=7, 'O+'

class MedicalRecord(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    tests=models.ManyToManyField(Test, related_name="medical_records")
    prognosis=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(blank=True, null=True)
    deleted_at=models.DateTimeField(null=True, blank=True)
    age=models.IntegerField(null=False, blank=False)
    height=models.IntegerField(null=False, blank=False)
    weight=models.IntegerField(null=False, blank=False)
    hiv_status=models.SmallIntegerField(choices=HIVStatus.choices)
    blood_group=models.SmallIntegerField(choices=BloodGroup.choices)
    body_temperature=models.IntegerField(null=False, blank=False)

    
    body_mass_index=models.IntegerField(null=False, blank=False)
    blood_pressure=models.CharField(null=False, blank=False)

    def __str__(self):
        return f"Record {self.id}"
    
class RecordOwnership(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    doctor_id=models.UUIDField(blank=True, null=True)
    patient_id=models.UUIDField(blank=True, null=True)
    record=models.ForeignKey(MedicalRecord, on_delete=models.DO_NOTHING)