from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.utils import timezone

from .models import NextOfKin, Guardianship, Dependent, Patient
from .validators import DatesValidator

dob_validator=DatesValidator()

class NextOfKinSerializer(serializers.ModelSerializer):
    class Meta:
        model=NextOfKin
        fields=['id', 'first_name', 'last_name', 'phone', 'email', 'relationship', 'created_at', 'updated_at', 'deleted_at']
        read_only_fields=['id', 'created_at', 'updated_at', 'deleted_at']

class PatientSerializer(serializers.ModelSerializer):
    password= serializers.CharField(write_only=True, required=False, validators=[validate_password])
    next_of_kin=NextOfKinSerializer(many=False, required=False)
    email=serializers.EmailField(required=False)
    class Meta:
        model=Patient
        fields=['id', 'first_name', 'last_name', 'surname', 'next_of_kin', 'email', 'phone', 'id_number', 'occupation', 'gender', 'residence', 'password', 'date_joined', 'updated_at', 'deleted_at']
        read_only_fields=['id', 'date_joined', 'updated_at', 'deleted_at']

    def create(self, validated_data):
        next_of_kin_data=validated_data.pop('next_of_kin', None)

        if next_of_kin_data:
            next_of_kin_obj=NextOfKin.objects.create(**next_of_kin_data)
            patient=Patient.objects.create_user(
                next_of_kin=next_of_kin_obj,
                **validated_data
            )
            return patient
        
        patient=Patient.objects.create_user(**validated_data)
        return patient
    
    def update(self, instance, validated_data):
        password=validated_data.pop('password', None)

        updated_next_of_kin=validated_data.pop('next_of_kin', None)

        if updated_next_of_kin:
            next_of_kin=instance.next_of_kin

            if next_of_kin is None:
                new_next_of_kin=NextOfKin.objects.create(**updated_next_of_kin)
                instance.next_of_kin=new_next_of_kin
            elif next_of_kin is not None:
                for attribute, value in updated_next_of_kin.items():
                    setattr(next_of_kin, attribute, value)

                    next_of_kin.updated_at=timezone.now()
                    next_of_kin.save()
        if password:
            pass

        instance.updated_at=timezone.now()
        return super().update(instance, validated_data)

class MinorPatientSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(required=False)
    phone=serializers.CharField(required=False)
    class Meta:
        model=Dependent
        fields=['id','first_name','last_name','surname','age','is_underage','email','phone', 'gender', 'date_of_birth','created_at','updated_at']
        read_only_fields=['id','age','is_underage','created_at','updated_at']

class GuardianshipSerializer(serializers.Serializer):
    id=serializers.UUIDField(read_only=True, required=False)
    relationship=serializers.CharField(required=True)
    dependent=MinorPatientSerializer(required=True, many=False)
    guardian=serializers.UUIDField(required=False)
    is_chaperone=serializers.BooleanField(required=False, read_only=True)
    created_at=serializers.DateTimeField(required=False, read_only=True)
    updated_at=serializers.DateTimeField(required=False, read_only=True)


    def create(self, validated_data:dict):
        dependent_data_obj:dict=validated_data.pop("dependent",None)
        if dependent_data_obj is None:
            raise serializers.ValidationError("Please provide patient data.")
        relationship=validated_data.get("relationship")
        if relationship is None:
            raise serializers.ValidationError("Please provide a relationship between the guardian and patient")
        
        if relationship.lower() not in ["mother","father","guardian"]:
            raise serializers.ValidationError("The relationship entries recognized are father, mother or guardian")
        validated_data['relationship'] = Guardianship.RepationshipTypes.find(relationship)
        validated_data['is_chaperone'] = (relationship in ['father', 'mother'])
        dob=dependent_data_obj.get("date_of_birth")
        if dob is None:
            raise serializers.ValidationError("Please provid a valid date of birth")
        validator=DatesValidator()
        dependent_data_obj["date_of_birth"]=validator.validate_dob(dob)
        guardian_id=validated_data.pop('guardian')
        guardian_obj=Patient.objects.get(id=guardian_id)
        patient=Dependent.objects.create(**dependent_data_obj)
        guardian=Guardianship.objects.create(
            dependent=patient,
            guardian=guardian_obj,
            **validated_data)
        return guardian

    def update(self, instance, validated_data:dict):
        dependent_data_obj:dict=validated_data.pop("dependent",None)
        
        
        relationship=validated_data.get("relationship")

        if relationship:
            if relationship.lower() not in ["mother","father","guardian"]:
                raise serializers.ValidationError("The relationship entries recognized are father, mother or guardian")
            instance.relationship = Guardianship.RepationshipTypes.find(relationship)
            instance.is_chaperone = (relationship in ['father', 'mother'])

        dob=dependent_data_obj.get("date_of_birth")

        if dob:
            validator=DatesValidator()
            dependent_data_obj["date_of_birth"]=validator.validate_dob(dob)

        dependent=instance.dependent
        for attribute, value in dependent_data_obj.items():
            setattr(dependent, attribute, value)
            dependent.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class ListPatientSerializer(serializers.ModelSerializer):
    gender=serializers.CharField(read_only=True, source="get_gender_display")
    next_of_kin=NextOfKinSerializer()
    class Meta:
        model=Patient
        fields=['id', 'first_name', 'last_name', 'surname', 'next_of_kin', 'email', 'phone', 'id_number', 'occupation', 'gender', 'residence', 'date_joined', 'updated_at', 'deleted_at']
        read_only_fields=['id', 'date_joined', 'updated_at', 'deleted_at']

class PasswordUpdateSerializer(serializers.ModelSerializer):
    old_password= serializers.CharField(required=True)
    new_password=serializers.CharField(required=True, validators=[validate_password])

    class Meta:
        model=Patient
        fields=['old_password', 'new_password']

class PasswordResetSerializer(serializers.ModelSerializer):
    new_password=serializers.CharField(required=True, validators=[validate_password])

    class Meta:
        model=Patient
        fields=['new_password']

class AuthSerializer(serializers.Serializer):
    email=serializers.EmailField(required=False, write_only=True)
    id_number=serializers.CharField(required=False, write_only=True)
    phone=serializers.CharField(required=False, write_only=True)
    password=serializers.CharField(
        label=('Password'),
        trim_whitespace=False,
        style={'input_type':'password'},
        write_only=True
    )


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username', None)
        self.username=None
        

    def get_token(cls, patient):
        token=RefreshToken.for_user(patient)

        token['is_superuser']=patient.is_superuser
        token['is_staff']=patient.is_staff
        token['is_active']=patient.is_active
        token['user_id']=str(patient.id)
        token['iss']=settings.SIMPLE_JWT['ISSUER']
        token['aud']=settings.SIMPLE_JWT['AUDIENCE']
        token['role']='patient'

        return token

    def validate(self, attrs):
        auth_fields=['phone', 'id_number', 'email']
        provided_fields=[field for field in auth_fields if attrs.get(field)]

        if len(provided_fields) <1:
            raise ValueError("Please provide a valid phone, email addresss or national id/passport number")
        if len(provided_fields) >1:
            raise ValueError("Only one of phone, email addresss or national id/passport number is needed")
        
        identifier_field=provided_fields[0]
        identifier_value=attrs[identifier_field]
        password=attrs['password']

        try:
            user=Patient.objects.get(**{identifier_field:identifier_value})
        except Patient.DoesNotExist as e:
            raise serializers.ValidationError({"detail":"Unable to login with provided credentials"}, code='authorization')

        if not user.check_password(password):
            raise serializers.ValidationError({"detail":"Unable to login with provided credentials"}, code='authorization')
        
        if not user.is_active:
            raise serializers.ValidationError({"detail":"User account is inactive"})
            

        self.user=user
        
        data={}
        refresh=self.get_token(self.user)
        data['refresh']=str(refresh)
        data['access']=str(refresh.access_token)

        return data

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

class UniqueDetailsAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model=Patient
        fields=['email', 'id_number', 'phone']

    def to_representation(self, instance):
        result = {}
        validated_data = self.validated_data
        
        if 'email' in validated_data:
            result['email_exists'] = self.Meta.model.objects.filter(email__iexact=validated_data['email']).exists()
        if 'id_number' in validated_data:
            result['id_number_exists'] = self.Meta.model.objects.filter(id_number__iexact=validated_data['id_number']).exists()
        if 'phone' in validated_data:
            result['phone_exists'] = self.Meta.model.objects.filter(phone__iexact=validated_data['phone']).exists()
        
        return result
