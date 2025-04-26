from django.db import models
from uuid import uuid4
from django.utils import timezone
from datetime import timedelta


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, unique=True, editable=False)
    user_id = models.CharField(max_length=255, unique=True)
    face_img=models.CharField(max_length=255)
    practicing_certificate=models.CharField(max_length=255)
    identity_card=models.CharField(max_length=255)
    valid_practicing_certificate=models.BooleanField(default=False)
    valid_identity_card=models.BooleanField(default=False)
    valid_face_img=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table='users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['created_at']),
        ]

    def validate_practicing_certificate(self):
        self.valid_practicing_certificate=True
        self.save()

    def invalidate_practicing_certificate(self):
        self.valid_practicing_certificate=False
        self.save()
    
    def validate_face_image(self):
        self.valid_face_img=True
        self.save()

    def invalidate_face_image(self):
        self.valid_face_img=False
        self.save()
    
    def validate_identity_card(self):
        self.valid_identity_card=True
        self.save()
    
    def invalidate_identity_card(self):
        self.valid_identity_card=False
        self.save()


class License(models.Model):
    class LicenseStatus(models.IntegerChoices):
        PENDING=0, 'Pending',
        APPROVED=1, 'Approved',
        DISAPPROVED=2,'Disapproved',
        SUSPENDED=3, 'Suspended',
        CANCELLED=4, 'Cancelled'
    id = models.UUIDField(primary_key=True, default=uuid4, unique=True, editable=False)
    status = models.IntegerField(choices=LicenseStatus.choices, default=LicenseStatus.PENDING)
    expiration_date = models.DateTimeField()
    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='license')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def practicing_certificate_is_valid(self):
        return self.user.valid_practicing_certificate
    
    @property
    def identity_card_is_valid(self):
        return self.user.valid_identity_card
    
    @property
    def face_verification(self):
        return self.user.valid_face_img

    @property
    def is_valid(self):
        return self.status == self.LicenseStatus.APPROVED and self.face_verification and self.practicing_certificate_is_valid and self.identity_card_is_valid and not self.is_expired()

    class Meta:
        db_table = 'licenses'
        verbose_name = 'License'
        verbose_name_plural = 'Licenses'
        ordering = ['expiration_date']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['expiration_date']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(expiration_date__gt=models.F('created_at')),
                name='expiration_date_gt_created_at'
            ),
        ]

    def __str__(self):
        return f"{self.status} License for user {self.user_id}"
    
    def grant_license(self):
        if self.status==self.LicenseStatus.DISAPPROVED:
            raise ValueError("This license has already been cancelled")
        
        if self.status == self.LicenseStatus.CANCELLED:
            raise ValueError("This license has been permanently cancelled")
        
        if self.practicing_certificate_is_valid and self.identity_card_is_valid and self.face_verification:
            self.status=self.LicenseStatus.APPROVED
            self.save()
        else:
            raise ValueError("License cannot be granted. All verifications must be valid.")

        return self

    def suspend_license(self):
        if self.status==self.LicenseStatus.CANCELLED or self.status==self.LicenseStatus.DISAPPROVED:
            raise ValueError("License has been permanently cancelled")
        if self.status==self.LicenseStatus.PENDING:
            raise ValueError("License has not been approved yet")
        if self.status==self.LicenseStatus.SUSPENDED:
            raise ValueError("License has already been suspended")
        self.status=self.LicenseStatus.SUSPENDED
        self.save()
        return self

    def cancel_license(self):
        if self.status==self.LicenseStatus.CANCELLED:
            raise ValueError("License has been permanently cancelled")
        if self.status==self.LicenseStatus.PENDING:
            raise ValueError("License has not been approved yet")
        if  self.status==self.LicenseStatus.DISAPPROVED:
            raise ValueError("The licence application was rejected")
        
        self.status=self.LicenseStatus.CANCELLED
        self.save()
        return self

    def disapprove_licence(self):
        if self.status==self.LicenseStatus.APPROVED or self.status==self.LicenseStatus.SUSPENDED or self.status==self.LicenseStatus.CANCELLED:
            raise ValueError("This application has already proceeded beyond this stage.")
        
        if  self.status==self.LicenseStatus.PENDING:
            self.status=self.LicenseStatus.DISAPPROVED
            self.save()
        elif self.status==self.LicenseStatus.DISAPPROVED:
            raise ValueError("This application has already been disapproved.")
        return self
    
    def extend_license(self, days):
        if self.status==self.LicenseStatus.CANCELLED or self.status==self.LicenseStatus.DISAPPROVED:
            raise ValueError("License has been permanently cancelled")
        if self.status==self.LicenseStatus.PENDING:
            raise ValueError("License has not been approved yet")
        if self.status==self.LicenseStatus.SUSPENDED:
            raise ValueError("License has been suspended")
        
        self.expiration_date+=timedelta(days=days)
        self.save()
        return self
    
    def revoke_license(self):   
        if self.status==self.LicenseStatus.CANCELLED or self.status==self.LicenseStatus.DISAPPROVED:
            raise ValueError("License has been permanently cancelled")
        if self.status==self.LicenseStatus.PENDING:
            raise ValueError("License has not been approved yet")
        if self.status==self.LicenseStatus.SUSPENDED:
            raise ValueError("License has been suspended")
        
        self.status=self.LicenseStatus.DISAPPROVED
        self.save()
        return self
    
    def is_expired(self):
        return timezone.now() > self.expiration_date
    
