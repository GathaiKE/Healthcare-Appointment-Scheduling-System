from rest_framework import serializers, status
from django.contrib.auth import password_validation
from rest_framework.response import Response

from .utilities import RegDetailsValidator, PasswordValidator,UserRoles, DataFetcher, UserDataManager
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
        
        verification_response=self.verify_data(validated_data=validated_data, request=request, role=role)
        validated_data["email"]=verification_response['email']
        validated_data["id_number"]=verification_response['id_number']
        validated_data["phone"]=verification_response['phone']
        
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
    

    def verify_data(self, validated_data, request, role:UserRoles):
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
        
        data_validator = RegDetailsValidator(service=verification_service, request=request)
        data_validity, err = data_validator.validate(validated_data)

        if not data_validity and err:
            raise serializers.ValidationError(err['detail'])
        return validated_data
    

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
    

class PasswordChangeSerializer(serializers.Serializer):
    old_password=serializers.CharField(
        label=('old_password'),
        trim_whitespace=False,
        style={'input_type':'password'},
        write_only=True,
        required=True
    )
    new_password=serializers.CharField(
        label=('new_password'),
        trim_whitespace=False,
        style={'input_type':'password'},
        write_only=True,
        required=True
    )

class PasswordResetSerializer(serializers.Serializer):
    new_password=serializers.CharField(
        label=('new_password'),
        trim_whitespace=False,
        style={'input_type':'password'},
        write_only=True,
        required=True,
    )