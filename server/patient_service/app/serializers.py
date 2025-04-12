from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.conf import settings

Patient=get_user_model()

class AdminSerializer(serializers.ModelSerializer):
    pass

class PatientSerializer(serializers.ModelSerializer):
    password= serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model=Patient
        fields=['id', 'first_name', 'last_name', 'surname', 'email', 'phone', 'id_number', 'password', 'date_joined', 'updated_at', 'deleted_at']
        read_only_fields=['id', 'date_joined', 'updated_at', 'deleted_at']

    def create(self, validated_data):
        patient=Patient.objects.create_user(
            first_name=validated_data
            ['first_name'],
            last_name=validated_data['last_name'],
            surname=validated_data['surname'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            password=validated_data['password'],
            id_number=validated_data['id_number']
        )
        return patient
    
    def update(self, instance, validated_data):
        password=validated_data.pop('password', None)
        if password:
            pass
        return super().update(instance, validated_data)

class PasswordUpdateSerializer(serializers.ModelSerializer):
    old_password= serializers.CharField(required=True)
    new_password=serializers.CharField(required=True, validators=[validate_password])

    class Meta:
        model=Patient
        fields=['old_password', 'new_password']

class AuthSerializer(TokenObtainPairSerializer):
    email=serializers.EmailField(
        label=('Email'),
        write_only=True
    )
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

    def get_token(cls, patient):
        token= super().get_token(patient)

        token['is_superuser']=patient.is_superuser
        token['is_staff']=patient.is_staff
        token['is_active']=patient.is_active
        token['user_id']=str(patient.id)
        token['iss']=settings.SIMPLE_JWT['ISSUER']
        token['aud']=settings.SIMPLE_JWT['AUDIENCE']
        token['role']='patient'

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
            raise serializers.ValidationError({"detail":"Unable to login with provided credentials"}, code='authorization')
        
        data={}
        refresh=self.get_token(self.user)
        data['refresh']=str(refresh)
        data['access']=str(refresh.access_token)

        return data
