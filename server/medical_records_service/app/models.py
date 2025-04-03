from django.db import models
import uuid

class Test(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    name=models.CharField(max_length=100, blank=False, null=False)
    result=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_ad=models.DateTimeField(auto_add=True, blank=True)
    deleted_at=models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

class MedicalRecord(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    tests=models.ManyToManyField(Test, related_name="medical_records")
    prognosis=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_ad=models.DateTimeField(auto_add=True, blank=True)
    deleted_at=models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Record {self.id}"