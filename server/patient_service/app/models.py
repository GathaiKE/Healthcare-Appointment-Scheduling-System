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
    
class InsuranceProvider(models.Model):
    id=models.UUIDField(unique=True, editable=False, primary_key=True, default=uuid.uuid4)
    name=models.CharField(blank=False, max_length=200)
    profile=models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name

class NextOfKin(models.Model):
    id=models.UUIDField(unique=True, default=uuid.uuid4, primary_key=True, editable=False)
    first_name=models.CharField(max_length=200, null=False, blank=False)
    last_name=models.CharField(max_length=200, null=False, blank=False)
    phone=models.CharField(max_length=12, blank=False, null=False)
    email=models.EmailField(null=True, blank=True)
    relationship=models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Patient(AbstractUser):
    class Gender(models.IntegerChoices):
        MALE=0, 'male',
        FEMALE=1, 'female'
    id=models.UUIDField(unique=True, editable=False, primary_key=True, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=12, unique=True, blank=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    surname = models.CharField(max_length=100, null=True)
    id_number=models.CharField(max_length=100, blank=False, default='123', unique=True)
    insurance_provider=models.ForeignKey(InsuranceProvider, on_delete=models.CASCADE, null=True)
    next_of_kin=models.ForeignKey(NextOfKin, on_delete=models.CASCADE, null=True)
    gender=models.IntegerField(choices=Gender.choices, null=False, blank=False)
    updated_at=models.DateTimeField(blank=True, null=True)
    occupation=models.CharField(max_length=200, null=True, blank=True)
    residence=models.CharField(max_length=200, null=True, blank=True)
    deleted_at=models.DateTimeField(null=True, blank=True)
    updated_at=models.DateTimeField(null=True, blank=True)
    username = None

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    objects = PatientManager()

    def __str__ (self):
        return f"{self.first_name or ''} {self.last_name or ''} {self.surname or ''}"

