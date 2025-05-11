from rest_framework import serializers, status
from django.contrib.auth import password_validation
from rest_framework.response import Response

from .utilities import EmailValidator, PasswordValidator,UserRoles, DataFetcher, UserDataManager
from .producer import register_admin, register_doctor, register_patient

class BaseUserSerializer(serializers.Serializer):
    id=serializers.UUIDField(read_only=True)
    first_name=serializers.CharField(required=True)
    last_name=serializers.CharField(required=True)
    surname=serializers.CharField(required=True)
    email=serializers.EmailField(required=True)
    phone=serializers.CharField(required=True)
    password=serializers.CharField(write_only=True, required=True, validators=[password_validation.validate_password])
    profile=serializers.CharField(required=False)
    id_number=serializers.CharField(required=True)
    date_joined=serializers.DateTimeField(read_only=True)
    updated_at=serializers.DateTimeField(read_only=True)
    deleted_at=serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        role=validated_data.pop('role', UserRoles.PUBLIC)
        if not role:
            raise ValueError("A recognized user role is required.")
        if role not in UserRoles:
            raise ValueError("The role provided is not recognized by the system.")
        
        email_value, email_err =self.validate_email(validated_data.get('email'), role)
        if email_value is None and email_err:
            return email_err
        pass_value, pass_error=self.validate_password(validated_data.get('password'))
        if pass_value is None and pass_error:
            return pass_error
        
        if role==UserRoles.PATIENT:
            register_patient(validated_data)
        elif role==UserRoles.DOCTOR:
            register_doctor(validated_data)
        elif role==UserRoles.STAFF or role==UserRoles.ADMIN or role==UserRoles.SUPERADMIN:
            validated_data.add('role', role)
            register_admin(validated_data)
        else:
            raise ValueError("User role provided is incorrect or invalid")

        return validated_data
    
    def update(self, instance, validated_data):
        role=validated_data.pop('role', UserRoles.PUBLIC)
        if not role:
            raise ValueError("A recognized user role is required.")
        if role not in UserRoles:
            raise ValueError("The role provided is not recognized by the system.")
        
        fetcher=DataFetcher()
        manager=UserDataManager()

        if role==UserRoles.PATIENT:
            user, err=fetcher.fetch_patient_detail(instance.id)
        elif role==UserRoles.DOCTOR:
            user, err=fetcher.fetch_doctor_detail(instance.id)
        elif role==UserRoles.STAFF or role==UserRoles.ADMIN or role==UserRoles.SUPERADMIN:
            user, err=fetcher.fetch_admin_detail(instance.id)
        else:
            raise ValueError("User role provided is incorrect or invalid")
        
        if err and user is None:
            return err
        

        email_value, email_err =self.validate_email(validated_data.get('email'), role)
        if email_value  and email_err is None:
            return Response({"detail":"User not found"})
        
        password=validated_data.pop('password', None)
        if password:
            pass
        
        if role==UserRoles.PATIENT:
            manager.update_patient(self.request,validated_data)
        elif role==UserRoles.DOCTOR:
            manager.update_doctor(self.request,validated_data)
        elif role==UserRoles.STAFF or role==UserRoles.ADMIN or role==UserRoles.SUPERADMIN:
            validated_data.add('role', role)
            manager.update_admin(self.request,validated_data)
        else:
            raise ValueError("User role provided is incorrect or invalid")

        return validated_data

    def validate_email(self, value, role:UserRoles):
        if not role:
            raise ValueError("A user role is needed to verify account ownership.")
        if role not in UserRoles:
            raise ValueError("The role provided is not recognized by the system.")
        from django.conf import settings

        base_url=settings.BASE_URL
        if role==UserRoles.PATIENT or role==UserRoles.PUBLIC:
            verification_suffix='patients'
        elif role==UserRoles.DOCTOR:
            verification_suffix='doctors'
        elif role==UserRoles.STAFF or role==UserRoles.ADMIN or role==UserRoles.SUPERADMIN:
            verification_suffix='admins'
        else:
            verification_suffix=None

        if verification_suffix is None:
            raise ValueError("You cannot register a public member")
        
        email_validator = EmailValidator(service_address=f"{base_url}/{verification_suffix}/")
        is_available, err = email_validator.validate(value)

        if not is_available:
            return None, err
        return value, None
    
    def validate_password(self, value):
        password_validator=PasswordValidator()
        is_valid, err = password_validator.validate(value)

        if not is_valid:
            return None, Response({"error":f"Password validation error: {err}"})
        return value, None

class DoctorDataSerializer(BaseUserSerializer):
    specialization=serializers.CharField(required=True)
    role=serializers.HiddenField(default=UserRoles.DOCTOR)
    
class AdminSerializer(BaseUserSerializer):
    role=serializers.HiddenField(default=UserRoles.STAFF)

class NextOfKinSerializer(serializers.Serializer):
    class Meta:
        fields=['id', 'first_name', 'last_name', 'phone', 'email', 'relationship', 'created_at', 'updated_at', 'deleted_at']
        read_only_fields=['id', 'created_at', 'updated_at', 'deleted_at']

class PatientSerializer(BaseUserSerializer):
    next_of_kin=NextOfKinSerializer(required=True, many=False)
    occupation=serializers.CharField()
    residence=serializers.CharField()
    role=serializers.HiddenField(default=UserRoles.PATIENT)


class AuthenticationDataSerializer(serializers.Serializer):
    email=serializers.EmailField(
        label=('Email'),
        write_only=True,
        required=True
    )
    password=serializers.CharField(
        label=('Password'),
        trim_whitespace=False,
        style={'input_type':'password'},
        write_only=True,
        required=True
    )