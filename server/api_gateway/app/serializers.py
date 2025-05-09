from rest_framework import serializers
from django.contrib.auth import password_validation
from rest_framework.response import Response

from .utilities import EmailValidator, PasswordValidator

class DoctorDataSerializer(serializers.Serializer):
    first_name=serializers.CharField(required=True, null=False, blank=False)
    last_name=serializers.CharField(required=True, null=False, blank=False)
    surname=serializers.CharField(required=True, null=False, blank=False)
    email=serializers.EmailField(required=True, null=False, blank=False)
    phone=serializers.CharField(required=True, null=False, blank=False)
    specialization=serializers.CharField(required=True, null=False, blank=False)
    password=serializers.CharField(write_only=True, required=False, validators=[password_validation.validate_password])
    profile=serializers.CharField(required=False, null=True, blank=True)
    id_number=serializers.CharField(required=True, null=False, blank=False)

    def validate_email(self, value):
        from django.conf import settings

        base_url=settings.BASE_URL
        email_validator = EmailValidator(service_address=f"{base_url}/doctors/")
        is_available, err = email_validator.validate(value)

        if not is_available:
            return err
        return value
    
    def validate_password(self, value):
        password_validator=PasswordValidator()
        is_valid, err = password_validator.validate(value)

        if not is_valid:
            return Response({"error":f"Password validation error: {err}"})
        return value