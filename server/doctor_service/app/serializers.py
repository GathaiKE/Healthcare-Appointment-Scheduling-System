from rest_framework import serializers
from django.contrib.auth import password_validation, get_user_model, authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings
# from celery import Celery

# app=Celery('doctor_service', broker=settings.CELERY_BROKER_URL)

from .models import Specialization
from .signals import create_schedue

Doctor=get_user_model()

class DoctorSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True, required=False, validators=[password_validation.validate_password])

    class Meta:
        model=Doctor
        fields=['id', 'first_name','last_name', 'surname', 'email', 'phone', 'specialization', 'password', 'profile', 'id_number', 'updated_at', 'deleted_at']
        read_only_fields=['id', 'updated_at', 'deleted_at']

    def create(self, validated_data):
        doctor=Doctor.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            surname=validated_data['surname'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            id_number=validated_data['id_number'],
            profile=validated_data['profile'] if validated_data['profile'] else "default",
            specialization=validated_data['specialization'],
            password=validated_data['password']
        )

        # app.send_task('appointment_service.tasks.create_doctor_calender', args=[doctor.id])
        create_schedue(doctor_id=doctor.id)

        return doctor
    
    def update(self, instance, validated_data):
        password=validated_data.pop('password', None)
        if password:
            pass
        return super().update(instance, validated_data)
    
class PasswordUpdateSerializer(serializers.ModelSerializer):
    old_password= serializers.CharField(required=True)
    new_password=serializers.CharField(required=True, validators=[password_validation.validate_password])

    class Meta:
        model=Doctor
        fields=['old_password', 'new_password']

class PasswordResetSerializer(serializers.ModelSerializer):
    new_password=serializers.CharField(required=True, validators=[password_validation.validate_password])

    class Meta:
        model=Doctor
        fields=['new_password']

class AuthSerializer(TokenObtainPairSerializer):
    email=serializers.EmailField(label=('Email'), write_only=True)
    password=serializers.CharField(
        label=('Password'),
        trim_whitespace=False,
        style={'input_type':'password'},
        write_only=True
    )
    username_field='email'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field]=serializers.EmailField(label=('Email'), write_only=True)


    def get_token(cls, doctor):
        token=super().get_token(doctor)

        token['is_superuser']=doctor.is_superuser
        token['is_staff']=doctor.is_staff
        token['is_active']=doctor.is_active
        token['user_id']=str(doctor.id)
        token['iss']=settings.SIMPLE_JWT['ISSUER']
        token['aud']=settings.SIMPLE_JWT['AUDIENCE']
        token['role']='doctor'

        return token
    
    def validate(self, attrs):
        authenticate_kwargs={
            'email': attrs['email'],
            'password': attrs['password']
        }

        try:
            authenticate_kwargs['request']=self.context['request']
        except KeyError:
            pass

        self.user=authenticate(**authenticate_kwargs)

        if not self.user:
            raise serializers.ValidationError({"detail":"Unable to log in with provided credentials"}, code='authorization')
        
        data={}
        refresh=self.get_token(self.user)
        data['refresh']=str(refresh)
        data['access']=str(refresh.access_token)

        return data

class SpecializationSeriaizer(serializers.ModelSerializer):
    class Meta:
        model=Specialization
        fields=['id','title']
        read_only_fields=['id']
