from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import uuid
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from .validators import DatesValidator

dob_validator=DatesValidator()

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
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(null=True, blank=True)
    deleted_at=models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class PatientManager(BaseUserManager):
    def create_user(self, id_number, phone, password=None, **extra_fields):
        if not id_number:
            raise ValueError("A national ID or passport number is required")
        if not phone:
            raise ValueError("A phone number is required")
        email=extra_fields.pop('email', None)
        if email:
            email=self.normalize_email(email)

        user = self.model(id_number=id_number, phone=phone, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        
        return user

class Patient(AbstractUser):
    class Gender(models.IntegerChoices):
        MALE=0, 'male',
        FEMALE=1, 'female'
    id=models.UUIDField(unique=True, editable=False, primary_key=True, default=uuid.uuid4)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    surname = models.CharField(max_length=100, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=12, unique=True, blank=False, null=False)
    id_number=models.CharField(max_length=100, blank=False, unique=True, null=False)
    insurance_provider=models.ForeignKey(InsuranceProvider, on_delete=models.CASCADE, null=True)
    next_of_kin=models.OneToOneField(NextOfKin, on_delete=models.CASCADE, null=True)
    gender=models.IntegerField(choices=Gender.choices, null=False, blank=False)
    occupation=models.CharField(max_length=200, null=True, blank=True)
    residence=models.CharField(max_length=200, null=True, blank=True)
    updated_at=models.DateTimeField(null=True, blank=True)
    deleted_at=models.DateTimeField(null=True, blank=True)
    username = None

    USERNAME_FIELD='id_number'
    REQUIRED_FIELDS=['phone']

    objects = PatientManager()

    def __str__ (self):
        return f"{self.first_name or ''} {self.last_name or ''} {self.surname or ''}"

class Dependent(models.Model):
    class Gender(models.IntegerChoices):
        MALE=0, 'male',
        FEMALE=1, 'female'
    id=models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    first_name=models.CharField(null=False, blank=False)
    last_name=models.CharField(null=False, blank=False)
    surname=models.CharField(null=False, blank=False)
    email=models.EmailField(unique=True, null=True, blank=True)
    phone=models.CharField(unique=True, null=True, blank=True)
    gender=models.IntegerField(choices=Gender.choices, null=False, blank=False, default=Gender.MALE)
    date_of_birth=models.DateField(validators=[dob_validator.validate_dob], default='2000-10-10')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    @property
    def age(self):
        return relativedelta(timezone.now().date(),self.date_of_birth).years
    
    @property
    def is_underage(self):
        return self.age<18

    class Meta:
        db_table="dependents"
        verbose_name="Minor"
        verbose_name_plural="Minors"
        ordering=['created_at']

    def __str__ (self):
        return f"{self.first_name or ''} {self.last_name or ''} {self.surname or ''}"
    
class Guardianship(models.Model):
    class RepationshipTypes(models.TextChoices):
        FATHER='father', 'Father'
        MOTHER='mother', 'Mother'
        GUARDIAN='guardian', 'Guardian'

        @classmethod
        def find(cls, value):
            value = value.lower()
            for choice in cls.choices:
                if choice[0].lower() == value:
                    return choice[0]
            raise ValueError(f"Invalid relationship type: {value}")

    id=models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    dependent=models.ForeignKey(Dependent, on_delete=models.DO_NOTHING)
    guardian=models.ForeignKey(Patient, on_delete=models.DO_NOTHING)
    relationship=models.CharField(null=False, max_length=20, choices=RepationshipTypes.choices)
    is_chaperone=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        db_table='guardianships'
        verbose_name='guardianship'
        verbose_name_plural='guardianships'
        unique_together=[('dependent', 'relationship')]
        constraints=[
            models.UniqueConstraint(fields=['dependent', 'guardian'],name='unique_guardian_assignment'),
            models.CheckConstraint(check=~models.Q(relationship='guardian') | models.Q(is_chaperone=False),name='chaperone_must_be_parent')
        ]