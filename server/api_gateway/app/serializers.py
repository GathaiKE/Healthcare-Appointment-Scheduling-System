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
    gender=serializers.IntegerField(required=True)
    password=serializers.CharField(write_only=True, required=True, validators=[password_validation.validate_password])
    profile=serializers.CharField(required=False)
    id_number=serializers.CharField(required=True)
    date_joined=serializers.DateTimeField(read_only=True)
    updated_at=serializers.DateTimeField(read_only=True)
    deleted_at=serializers.DateTimeField(read_only=True)

    class Meta:
        fields = ["id","first_name","last_name","surname","email","phone","password","profile", "gender", "id_number","date_joined","updated_at","deleted_at"]

    def create(self, validated_data):
        role=validated_data.pop('role', None)
        request=self.context.get('request')

        if request is None:
            raise ValueError("No request headers provided.")
        
        if role is None:
            raise ValueError("A recognized user role is required.")
        
        if role not in [role for role in UserRoles]:
            raise ValueError("The role provided is not recognized by the system.")
        
        validated_email =self.check_email(value=validated_data.get('email'), request=request, role=role)
        
        validated_data["email"]=validated_email
        
        if role==UserRoles.PATIENT:
            register_patient(validated_data)
        elif role==UserRoles.DOCTOR:
            register_doctor(validated_data)
        elif role==UserRoles.STAFF or role==UserRoles.ADMIN or role==UserRoles.SUPERADMIN:
            validated_data['role']=role
            register_admin(validated_data)
        else:
            raise ValueError("User role provided is incorrect or invalid")

        return validated_data
    
    def update(self, instance, validated_data):
        role=validated_data.pop('role', None)
        request=self.context.get('request')


        if request is None:
            raise ValueError("No request headers provided.")
        if role is None:
            raise ValueError("A recognized user role is required.")
        if role not in [role.value for role in UserRoles]:
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
        

        validated_email=self.check_email(value=validated_data.get("email"), request=request, role=role)

        validated_data["email"]=validated_email
        
        password=validated_data.pop('password', None)
        if password is not None:
            pass
        
        if role==UserRoles.PATIENT:
            manager.update_patient(self.request,validated_data)
        elif role==UserRoles.DOCTOR:
            manager.update_doctor(self.request,validated_data)
        elif role==UserRoles.STAFF or role==UserRoles.ADMIN or role==UserRoles.SUPERADMIN:
            validated_data['role']=role
            manager.update_admin(self.request,validated_data)
        else:
            raise ValueError("User role provided is incorrect or invalid")

        return validated_data

    def check_email(self, value, request, role:UserRoles):
        if not role:
            return ValueError("A user role is needed to verify account ownership.")
        if role not in UserRoles:
            raise ValueError("The role provided is not recognized by the system.")
        
        if role==UserRoles.PATIENT:
            verification_service='patients'
        elif role==UserRoles.DOCTOR:
            verification_service='doctors'
        elif role==UserRoles.STAFF or role==UserRoles.ADMIN or role==UserRoles.SUPERADMIN:
            verification_service='admins'
        else:
            verification_service=None

        if verification_service is None:
            raise ValueError("You cannot register a public member")
        
        email_validator = EmailValidator(service=verification_service, request=request)
        is_available, err = email_validator.validate(value)

        if is_available and err is None:
            return value
        raise serializers.ValidationError({"detail":f"{err['error']}:{err['detail']}", "status":err.get('status', status.HTTP_400_BAD_REQUEST)})
    

class DoctorDataSerializer(BaseUserSerializer):
    specialization=serializers.CharField(required=True)
    role=serializers.HiddenField(default=UserRoles.DOCTOR)
    
class AdminSerializer(BaseUserSerializer):
    role=serializers.HiddenField(default=UserRoles.STAFF)

class NextOfKinSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    relationship = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

class PatientSerializer(BaseUserSerializer):
    next_of_kin=NextOfKinSerializer(required=True, many=False)
    occupation=serializers.CharField()
    residence=serializers.CharField()
    role=serializers.HiddenField(default=UserRoles.PATIENT)

    class Meta:
        fields = BaseUserSerializer.Meta.fields + [
            'next_of_kin', 'occupation', 'residence', 'role'
        ]


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
    