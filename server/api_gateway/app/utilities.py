import requests, re, json
from rest_framework import status, serializers
from rest_framework.response import Response


class ServiceAddress:
    def __init__(self, request_headers):
        from django.conf import settings
        self.request_headers=request_headers
        self.patients_base_url=settings.PATIENT_SERVICE_ADDRESS
        self.patients_endpoint=f"{self.patients_base_url}/patients"
        self.doctors_base_url=settings.DOCTOR_SERVICE_ADDRESS
        self.doctors_endpoint=f"{self.doctors_base_url}/doctors"
        self.admins_base_url=settings.ADMINISTRATOR_SERVICE_ADDRESS
        self.admins_endpoint=f"{self.admins_base_url}/admins"
        self.access_token=''
        self.refresh_token=''

    error_mapping = {
        400: ("Bad Request", "Invalid input data"),
        401: ("Unauthorized", "Invalid credentials"),
        403: ("Forbidden", "Account disabled or locked"),
        404: ("Not Found", "User account not found"),
        429: ("Too Many Requests", "Login attempts exceeded")
    }

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
            response=requests.get(url=f"{self.endpoint}/", params={'email':email}, timeout=timeout)
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

class Authenticator(ServiceAddress):
    def patient_login(self, validated_data):
        try:
            response=requests.post(f"{self.patients_endpoint}/login/", headers=self.request_headers, json=validated_data, timeout=5)

            if response.status_code == status.HTTP_201_CREATED:
                return {"data":response.json(), "status":status.HTTP_201_CREATED}, None

            error_mapping=self.error_mapping

            default_error = (f"HTTP {response.status_code}", json.loads(response.text).get('detail')[0])
            error_title, error_detail = error_mapping.get(
                response.status_code, 
                default_error
            )

            return None, {
                'error': error_title,
                'detail': error_detail,
                'status': response.status_code,
                'original_response': response.json() 
            }
        
        except requests.exceptions.Timeout:
            return None, {
                'error': 'Gateway Timeout',
                'detail': 'Patient service timed out',
                'status': status.HTTP_504_GATEWAY_TIMEOUT
            }

        except requests.exceptions.RequestException as e:
            return None, {
                'error': 'Service Unavailable',
                'detail': 'Patient service unavailable',
                'status': status.HTTP_503_SERVICE_UNAVAILABLE
            }

    def doctor_login(self, validated_data):
        try:
            response=requests.post(f"{self.doctors_endpoint}login/", headers=self.request_headers, json=validated_data, timeout=5)

            if response.status_code == status.HTTP_201_CREATED:
                return {"data":response.json(), "status":status.HTTP_201_CREATED}, None

            error_mapping = self.error_mapping

            default_error = (f"HTTP {response.status_code}", json.loads(response.text).get('detail')[0])
            error_title, error_detail = error_mapping.get(
                response.status_code, 
                default_error
            )

            return None, {
                'error': error_title,
                'detail': error_detail,
                'status': response.status_code,
                'original_response': response.json() 
            }
        
        except requests.exceptions.Timeout:
            return None, {
                'error': 'Gateway Timeout',
                'detail': 'PatiDoctorsent service timed out',
                'status': status.HTTP_504_GATEWAY_TIMEOUT
            }

        except requests.exceptions.RequestException as e:
            return None, {
                'error': 'Service Unavailable',
                'detail': 'Doctors service unavailable',
                'status': status.HTTP_503_SERVICE_UNAVAILABLE
            }

    def admin_login(self, validated_data):
        try:
            response=requests.post(f"{self.admins_endpoint}login/", headers=self.request_headers, json=validated_data, timeout=5)

            if response.status_code == status.HTTP_201_CREATED:
                return {"data":response.json(), "status":status.HTTP_201_CREATED}, None


            default_error = (f"HTTP {response.status_code}", json.loads(response.text).get('detail')[0])
            error_title, error_detail = self.error_mapping.get(
                response.status_code, 
                default_error
            )

            return None, {
                'error': error_title,
                'detail': error_detail,
                'status': response.status_code,
                'original_response': response.json() 
            }
        
        except requests.exceptions.Timeout:
            return None, {
                'error': 'Gateway Timeout',
                'detail': 'Administrator service timed out',
                'status': status.HTTP_504_GATEWAY_TIMEOUT
            }

        except requests.exceptions.RequestException as e:
            return None, {
                'error': 'Service Unavailable',
                'detail': 'Administrator service unavailable',
                'status': status.HTTP_503_SERVICE_UNAVAILABLE
            }

class DataFetcher(ServiceAddress):
    def fetch_patients(self):
        try:
            response=requests.get(f"{self.patients_endpoint}", None, headers=self.request_headers, timeout=5)
        except:
            return None, Response({"error":"Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if response.status_code==status.HTTP_200_OK:
            return {"data":response.json(), "status": status.HTTP_200_OK}, None
        
        default_error= (f"HTTP {response.status_code}", json.loads(response.text).get('detail')[0])
        title, detail=self.error_mapping.get(response.status_code, default_error)
        
        return None, {
            'error': title,
            'detail':detail,
            'status': response.status_code,
            'original_error': response.json()
        }

    def fetch_patient_detail(self, pk):
        try:
            response=requests.get(url=f"{self.patients_endpoint}/{pk}/", headers=self.request_headers)

            print(f"RESPONSE: {response}")

            if response.status_code==status.HTTP_200_OK:
                return {"data":response.json(), "status": response.status_code}, None
            
            default_error= (f"HTTP {response.status_code}", response.text)
            title, detail=self.error_mapping.get(response.status_code, default_error)
            
            return None, {
                'error': title,
                'detail':detail,
                'status': response.status_code,
                'original_error': response.json()
            }
        
        except requests.exceptions.RequestException as e:
            print(f"Network error: {str(e)}")
            return None, {
                "error": "Service Unavailable",
                "detail": "Patient service unreachable",
                "status": status.HTTP_503_SERVICE_UNAVAILABLE
            }

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return None, {
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR
            }
        
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
            response=requests.get(f"{self.doctors_endpoint}{doctor_id}/", None, headers=self.request_headers)
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
                timeout=2
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
            response=requests.delete(f"{self.patients_endpoint}/{patient_id}/", headers=self.request_headers, timeout=5)

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