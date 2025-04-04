from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid

class PatientManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        
        return user
    
    # def create_superuser(self, email, password, **extra_fields):
    #     extra_fields.setdefault('is_staff',True)
    #     extra_fields.setdefault('is_superuser',True)
    #     return self.create_user(email, password, **extra_fields)

class InsuranceProvider(models.Model):
    id=models.UUIDField(unique=True, editable=False, primary_key=True, default=uuid.uuid4)
    name=models.CharField(blank=False, max_length=200)
    profile=models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name

class Patient(AbstractUser):
    id=models.UUIDField(unique=True, editable=False, primary_key=True, default=uuid.uuid4)
    email = models.EmailField(unique=True, default='email@email.com')
    phone = models.CharField(max_length=12, unique=True, blank=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    surname = models.CharField(max_length=100, null=True)
    id_number=models.CharField(max_length=100, blank=False, default='123', unique=True)
    profile=models.CharField(max_length=200, null=True)
    insurance_provider=models.ForeignKey(InsuranceProvider, on_delete=models.CASCADE, null=True)
    updated_at=models.DateTimeField(blank=True, null=True)
    deleted_at=models.DateTimeField(null=True, blank=True)
    username = None

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    objects = PatientManager()

    def __str__ (self):
        return f"{self.first_name or ''} {self.last_name or ''} {self.surname or ''}"
    
class Doctor(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name=models.CharField(max_length=200, null=False, blank=False)
    reference_id=models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return self.name

class PatientVisits(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    patient=models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor=models.ForeignKey(Doctor, on_delete=models.CASCADE)
    record_id=models.CharField(max_length=100, blank=False, null=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Visit to {self.doctor} by {self.patient}"
