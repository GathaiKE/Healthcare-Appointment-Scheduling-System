import requests, re, json, jwt
from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from enum import Enum

class ServiceAddress:
    def __init__(self, request):
        from django.conf import settings
        self.request=request
        self.request_headers=request.headers
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
        404: ("Not Found", "Record not found"),
        429: ("Too Many Requests", "Request attempt limit exceeded")
    }

class PasswordValidator:     
    def validate(self, password, user=None):
            if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
                raise serializers.ValidationError("Password must be at least 8 characters long with 1 uppercase, 1 lowercase, 1 digit, and 1 special character (@$!%*?&)")
    
    def get_help_text(self):
        return ("Your password must contain at least 8 characters with a mix of uppercase, lowercase, numbers, and special characters (@$!%*?&).")

class EmailValidator(ServiceAddress):
    def __init__(self, request, service):
        super().__init__(request=request)
        self.service=service

    def validate(self, email):
        if str(self.service).lower() not in ['patients', 'doctors', 'admins']:
            return False, {"error":"Invalid address", "status":status.HTTP_400_BAD_REQUEST, "detail":"Service provided is not recognized"}

        if self.service=='doctors':
            validation_endpoint=self.doctors_endpoint
        elif self.service=='patients':
            validation_endpoint=self.patients_endpoint
        elif self.service=='admins':
            validation_endpoint=self.admins_endpoint
        else:
            validation_endpoint=None

        if validation_endpoint is None:
            return False, {"error":"Invalid address", "status":status.HTTP_400_BAD_REQUEST, "detail":f"{validation_endpoint} is not a valid address"}

        try:
            response=requests.get(url=f"{validation_endpoint}/check-email/", headers=self.request_headers, params={'email':email}, timeout=2.0)
            data=response.json()
            print(f"EMAIL VALIDATION RESPONSE: {data}")
            if response.status_code==status.HTTP_200_OK:
                    return True, None
            if response.status_code==status.HTTP_400_BAD_REQUEST:
                if data['email']:
                    return False, {"detail":data["email"], "error":"Bad Request", "status": status.HTTP_400_BAD_REQUEST}
                return False, {"detail":response.reason, "status": status.HTTP_400_BAD_REQUEST}
                
            default_error=f"HTTP {response.status_code}", response.text
            title, detail=self.error_mapping.get(response.status_code, default_error)
            return False, {
                "error": title,
                "detail":detail,
                "status":response.status_code,
                "original_error":response.json()
            }
        except Exception as e:
            return False, {"error":"Internal Server Error","detail":str(e), "status":status.HTTP_500_INTERNAL_SERVER_ERROR}

class UserRoles(Enum):
    PUBLIC=0,"public"
    PATIENT=1, "patient"
    DOCTOR=2, 'doctor'
    STAFF=3, 'staff'
    ADMIN=4, 'admin'
    SUPERADMIN=5, 'superuser'

class Authenticator(ServiceAddress, JWTAuthentication):
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

    def get_unvalidated_token(self, raw_token):
        return jwt.decode(raw_token, options={'verify_signature':False})
    
    def current_user(self):
        headers=self.get_header(self.request)
        if not headers:
            title, detail=self.error_mapping.get(401)
            return None, {'error':title,'detail':detail, 'status':status.HTTP_401_UNAUTHORIZED}
        
        try:
            raw_token=self.get_raw_token(headers)
            payload=self.get_unvalidated_token(raw_token)
        except Exception as e:
            return None, {
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "original_error": str(e)
            }
        
        issuer=payload.get('iss')

        issuer_routes={
            'patient_service':self.patients_endpoint,
            'doctor_service':self.doctors_endpoint,
            'administrator':self.admins_endpoint
        }

        route=issuer_routes.get(issuer)

        try:
            response=requests.get(f"{route}/me/", headers=self.request_headers, timeout=5)

            if response.status_code == status.HTTP_200_OK:
                return {
                    'data': response.json(),
                    'status': response.status_code
                }, None
            
            default_error=f"HTTP {response.status_code}", response.text
            error, detail = self.error_mapping.get(response.status_code, default_error)
            return None,{
                "error": error,
                'detail': detail,
                "status": response.status_code
            }
        
        except requests.exceptions.RequestException as e:
            return None, {
                "error": "Service Unavailable",
                "detail": "Patient service unreachable",
                "status": status.HTTP_503_SERVICE_UNAVAILABLE,
                "original_error": str(e)
            }

        except Exception as e:
            return None, {
                "error": "Internal Server Error",
                "detail": "An unexpected error occurred",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "original_error": str(e)
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
            return None, {
                "error": "Service Unavailable",
                "detail": "Patient service unreachable",
                "status": status.HTTP_503_SERVICE_UNAVAILABLE
            }

        except Exception as e:
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
