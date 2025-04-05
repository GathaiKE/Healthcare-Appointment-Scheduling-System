from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid

class DoctorManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        
        return user
    
class Specialization(models.Model):
    id=models.UUIDField(unique=True, editable=False, primary_key=True, default=uuid.uuid4)
    title=models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Doctor(AbstractUser):
    id=models.UUIDField(unique=True, editable=False, primary_key=True, default=uuid.uuid4)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    surname = models.CharField(max_length=100, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=12, unique=True, blank=True)
    id_number=models.CharField(max_length=100, blank=False)
    profile=models.CharField(max_length=200, null=True, blank=True)
    specialization=models.ForeignKey(Specialization, on_delete=models.CASCADE)
    updated_at=models.DateTimeField(blank=True, null=True)
    deleted_at=models.DateTimeField(null=True, blank=True)
    username = None

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    objects = DoctorManager()

    def __str__ (self):
        return f"{self.first_name or ''} {self.last_name or ''} {self.surname or ''}"
    
class Patient(models.Model):
    id=models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    name=models.CharField(max_length=200)
    patient_ref=models.CharField(max_length=200)
    record_ref=models.CharField(max_length=200)

    def __str__(self):
        return self.name

class DoctorPatient(models.Model):
    id=models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    patient=models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor=models.ForeignKey(Doctor, on_delete=models.CASCADE)

    def __str__(self):
        return f"Patient: {self.patient} - Doctor: {self.doctor}"


