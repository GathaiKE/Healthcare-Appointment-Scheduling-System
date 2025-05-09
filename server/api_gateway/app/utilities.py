import requests, re
from rest_framework import status, serializers
from rest_framework.response import Response

class PasswordValidator:
    def validate(self, password):
            if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
                return False, serializers.ValidationError("Password must be at least 8 characters long with 1 uppercase, 1 lowercase, 1 digit, and 1 special character (@$!%*?&)")
            return True, None

    def get_help_text(self):
        return ("Your password must contain at least 8 characters with a mix of uppercase, lowercase, numbers, and special characters (@$!%*?&).")


class EmailValidator:
    def __init__(self, service_address):
        self.service_address=service_address
        self.endpoint=f"{service_address}/check-email/"


    def validate(self, email, timeout=2.0):
        try:
            response=requests.get(url=self.endpoint, params={'email':email}, timeout=timeout)
        except Exception as e:
            return False, Response({"error":"Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        response.raise_for_status()
        data=response.json()
        if data['exists']:
            return False, Response("Email already exists", status=status.HTTP_403_FORBIDDEN)
        else:
            return True, None