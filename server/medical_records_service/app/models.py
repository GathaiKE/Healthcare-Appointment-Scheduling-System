from django.db import models
import uuid

class Test(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    name=models.CharField(max_length=100, blank=False, null=False)
    details=models.TextField(null=True, blank=True)
    result=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    deleted_at=models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class MedicalRecord(models.Model):
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
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    tests=models.ManyToManyField(Test, related_name="medical_records")
    prognosis=models.TextField()
    age=models.IntegerField(null=False, blank=False)
    height_m=models.FloatField(null=False, blank=False, help_text='Height in metres')
    weight_kg=models.FloatField(null=False, blank=False, help_text='Weight in kilograms')
    hiv_status=models.SmallIntegerField(choices=HIVStatus.choices, null=False, blank=False)
    blood_group=models.SmallIntegerField(choices=BloodGroup.choices, null=False, blank=False)
    body_temperature=models.IntegerField(null=False, blank=False)
    systolic_bp=models.PositiveSmallIntegerField(null=True, blank=True)
    diastolic_bp=models.PositiveSmallIntegerField(null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    deleted_at=models.DateTimeField(null=True, blank=True)

    @property
    def body_mass_index(self):
        if self.height_m and self.weight_kg:
            try:
                return round(self.weight_kg/(self.height_m**2), 2)
            except ZeroDivisionError:
                return None
        return None

    def __str__(self):
        return f"Record {self.id}"
    
class RecordOwnership(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    doctor_id=models.UUIDField(blank=True, null=True)
    patient_id=models.UUIDField(blank=True, null=True)
    record=models.ForeignKey(MedicalRecord, on_delete=models.DO_NOTHING)


# X-Ray and other scans upload by doctors.