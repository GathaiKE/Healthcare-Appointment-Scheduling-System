from django.contrib.auth import get_user_model
from rest_framework import serializers
import re
from django.utils import timezone
from django.core.exceptions import ValidationError


class PasswordValidator:     
    def validate(self, password, user=None):
            if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
                raise serializers.ValidationError("Password must be at least 8 characters long with 1 uppercase, 1 lowercase, 1 digit, and 1 special character (@$!%*?&)")
    
    def get_help_text(self):
        return ("Your password must contain at least 8 characters with a mix of uppercase, lowercase, numbers, and special characters (@$!%*?&).")


class DatesValidator:
     def validate_dob(self, value):
          if timezone.now().date() < value:
               raise ValidationError("Date of birth cannot be i the future")
          return value