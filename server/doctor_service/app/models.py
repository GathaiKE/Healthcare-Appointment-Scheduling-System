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
    description=models.CharField(max_length=200, null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(null=True)
    deleted_at=models.DateTimeField(null=True)

    def __str__(self):
        return self.title

    
# class License(models.Model):
#     class LicenseStatus(models.IntegerChoices):
#         PENDING=0, 'Pending',
#         APPROVED=1, 'Approved',
#         DISAPPROVED=2,'Disapproved',
#         SUSPENDED=3, 'Suspended',
#         CANCELLED=4, 'Cancelled'
#     id=models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
#     practicing_certificate_is_valid=models.BooleanField(default=False)
#     identity_card_is_valid=models.BooleanField(default=False)
#     face_verification=models.BooleanField(default=False)
#     status=models.IntegerField(choices=LicenseStatus.choices, default=LicenseStatus.PENDING)
#     created_at=models.DateTimeField(auto_now_add=True)
#     updated_at=models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.status

#     def grant_license(self):
#         if self.status==self.LicenseStatus.DISAPPROVED:
#             raise ValueError("This license has already been cancelled")
        
#         if self.status == self.LicenseStatus.CANCELLED:
#             raise ValueError("This license has been permanently cancelled")
        
#         if self.practicing_certificate_is_valid and self.identity_card_is_valid and self.face_verification:
#             self.status=self.LicenseStatus.APPROVED

#         return self

#     def suspend_license(self):
#         if self.status==self.LicenseStatus.CANCELLED or self.status==self.LicenseStatus.DISAPPROVED:
#             raise ValueError("License has been permanently cancelled")
#         if self.status==self.LicenseStatus.PENDING:
#             raise ValueError("License has not been approved yet")
#         if self.status==self.LicenseStatus.SUSPENDED:
#             raise ValueError("License has already been suspended")
#         self.status=self.LicenseStatus.SUSPENDED
#         return self

#     def cancel_license(self):
#         if self.status==self.LicenseStatus.CANCELLED:
#             raise ValueError("License has been permanently cancelled")
#         if self.status==self.LicenseStatus.PENDING:
#             raise ValueError("License has not been approved yet")
#         if  self.status==self.LicenseStatus.DISAPPROVED:
#             raise ValueError("The licence application was rejected")
        
#         self.status=self.LicenseStatus.CANCELLED
#         return self

#     def disapprove_licence(self):
#         if  self.status==self.LicenseStatus.PENDING:
#             self.status=self.LicenseStatus.DISAPPROVED
        
#         if self.status==self.LicenseStatus.APPROVED or self.status==self.LicenseStatus.SUSPENDED or self.status==self.LicenseStatus.CANCELLED:
#             raise ValueError("This application has already proceeded beyond this stage.")
#         return self
    
class Doctor(AbstractUser):
    id=models.UUIDField(unique=True, editable=False, primary_key=True, default=uuid.uuid4)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=12, blank=True)
    id_number=models.CharField(max_length=100, unique=True, blank=False, null=False)
    profile=models.CharField(max_length=200, null=True, blank=True)
    specialization=models.ForeignKey(Specialization, on_delete=models.CASCADE)
    # license=models.OneToOneField(License, on_delete=models.CASCADE)
    updated_at=models.DateTimeField(blank=True, null=True)
    username = None

    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]

    objects = DoctorManager()

    def __str__ (self):
        return f"{self.first_name or ''} {self.last_name or ''} {self.surname or ''}"

