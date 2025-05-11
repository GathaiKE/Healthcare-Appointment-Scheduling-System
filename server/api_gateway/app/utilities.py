import requests, re
from rest_framework import status, serializers
from rest_framework.response import Response
from django.db import models

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


class UserRoles:
    PUBLIC=0,"public"
    PATIENT=1, "patient"
    DOCTOR=2, 'doctor'
    STAFF=3, 'staff'
    ADMIN=4, 'admin'
    SUPERADMIN=5, 'superuser'

class Authenticator:
    def __init__(self, request_headers):
        from django.conf import settings
        self.request_headers=request_headers
        self.patients_base_url=settings.PATIENT_SERVICE_ADDRESS
        self.patients_endpoint=f"{self.patients_base_url}/patients/"
        self.doctors_base_url=settings.DOCTOR_SERVICE_ADDRESS
        self.doctors_endpoint=f"{self.doctors_base_url}/doctors/"
        self.admins_base_url=settings.ADMINISTRATOR_SERVICE_ADDRESS
        self.admins_endpoint=f"{self.admins_base_url}/admins/"

    def patient_login(self, validated_data):
        try:
            response=requests.post(f"{self.patients_endpoint}/login/", headers=self.request_headers, data=validated_data)
            print(f"LOGIN RESPONSE: {response.json()}")
            if response.status_code == 200:
                return response.json(), None
            return None, response.json()
        except ValueError as e:
            print(f"LOGIN ERROR: {e}")
            return None, Response({"error":"Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DataFetcher:
    def __init__(self, request_headers):
        from django.conf import settings
        self.request_headers=request_headers
        self.patients_base_url=settings.PATIENT_SERVICE_ADDRESS
        self.patients_endpoint=f"{self.patients_base_url}/patients/"
        self.doctors_base_url=settings.DOCTOR_SERVICE_ADDRESS
        self.doctors_endpoint=f"{self.doctors_base_url}/doctors/"
        self.admins_base_url=settings.ADMINISTRATOR_SERVICE_ADDRESS
        self.admins_endpoint=f"{self.admins_base_url}/admins/"
        self.access_token=''
        self.refresh_token=''

    def fetch_patients(self):
        try:
            response=requests.get(f"{self.patients_endpoint}", None, headers=self.request_headers)
            print(f"RESPONSE IN UTILITY FUNCT: {response}")
        except:
            return None, Response({"error":"Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if response.status_code ==200:
            return response.json(), None
        return None, response.json()

    def fetch_patient_detail(self, patient_id):
        try:
            response=requests.get(f"{self.patients_endpoint}/{patient_id}/", None, headers=self.request_headers)
        except:
            return None, Response({"error":"Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if response.status_code ==200:
            return response.json(), None
        return None, response

    def fetch_doctors(self):
        try:
            response=requests.get(f"{self.doctors_endpoint}", None, headers=self.request_headers)
        except:
            return None, Response({"error":"Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if response.status_code ==200:
            return response.json(), None
        return None, response
    
    def fetch_doctor_detail(self, doctor_id):
        try:
            response=requests.get(f"{self.doctors_endpoint}/{doctor_id}/", None, headers=self.request_headers)
        except:
            return None, Response({"error":"Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if response.status_code ==200:
            return response.json(), None
        return None, response
    
    def fetch_admins(self):
        try:
            response=requests.get(f"{self.admins_endpoint}", None, headers=self.request_headers)
        except:
            return None, Response({"error":"Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if response.status_code ==200:
            return response.json(), None
        return None, response
    
    def fetch_admin_detail(self, admin_id):
        try:
            response=requests.get(f"{self.admins_endpoint}/{admin_id}/", None, headers=self.request_headers)
        except:
            return None, Response({"error":"Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if response.status_code ==200:
            return response.json(), None
        return None, response
    
class UserDataManager(DataFetcher):
    def update_patient(self, request, validated_data):
        try:
            response=requests.put(
                f"{self.patients_endpoint}/{request.pk}/update/",
                headers=self.request_headers,
                data=validated_data,
                timeout='2.0'
            )
            return response, None
        except:
            return None, Response({"error":f"Internal server error: {response}"})

    def update_doctor(self, request, validated_data):
        try:
            response=requests.put(
                f"{self.doctors_endpoint}/{request.pk}/update/",
                headers=self.request_headers,
                data=validated_data,
                timeout='2.0'
            )
            return response, None
        except:
            return None, Response({"error":f"Internal server error: {response}"})
        
    def update_admin(self, request, validated_data):
        try:
            response=requests.put(
                f"{self.admins_endpoint}/{request.pk}/update/",
                headers=self.request_headers,
                data=validated_data,
                timeout='2.0'
            )
            return response, None
        except:
            return None, Response({"error":f"Internal server error: {response}"})   

    def delete_patient(self, patient_id):
        try:
            response=requests.delete(f"{self.patients_endpoint}/{patient_id}/", headers=self.request_headers)

            if response.status_code==204:
                return Response({"detail":"Patient deleted successfully"}, status=status.HTTP_204_NO_CONTENT), None
            return response, None
        except:
            return None, Response({"error":"Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete_doctor(self, doctor_id):
        try:
            response=requests.delete(f"{self.doctors_endpoint}/{doctor_id}/", headers=self.request_headers)

            if response.status_code==204:
                return Response({"detail":"Doctor deleted successfully"}, status=status.HTTP_204_NO_CONTENT), None
            return response, None
        except:
            return None, Response({"error":"Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete_admin(self, admin_id):
        try:
            response=requests.delete(f"{self.admins_endpoint}/{admin_id}/", headers=self.request_headers)

            if response.status_code==204:
                return Response({"detail":"Admin deleted successfully"}, status=status.HTTP_204_NO_CONTENT), None
            return response, None
        except:
            return None, Response({"error":"Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)