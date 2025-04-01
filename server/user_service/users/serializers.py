from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from django.conf import settings



User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    class Meta:
        model = User
        fields = ["id","first_name", "last_name", "surname", "email", "password", "phone", "date_joined"]
        read_only_fields = ["id", "date_joined"]

    def create(self, validated_data):
        user = User.objects.create_user(
            first_name= validated_data['first_name'],
            last_name = validated_data['last_name'],
            surname = validated_data['surname'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            password=validated_data['password']
        )

        return user
    
    def update(self, instance, validated_data):
        password=validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        return super().update(instance, validated_data)

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "is_staff", "is_active"]
        read_only_fields=["id"]
        extra_kwargs={
            'is_staff': {'required':False},
            'is_active': {'required':False}
        }

class PasswordUpdateSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    class Meta:
        model=User
        fields=["old_password", "new_password"]

class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label=('Email'), write_only=True)
    password = serializers.CharField(
        label=('Password'),
        trim_whitespace=False,
        style={'input_type': 'password'},
        write_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            if not user:
                raise serializers.ValidationError({"message":"Unable to login with provided credentials"}, code="authorization")
        else:
            raise serializers.ValidationError({"message":"Both email and password are required"}, code="authorization")
        
        attrs['user'] = user
        return attrs
    
class CustomTokenSerializer(TokenObtainSerializer):
    email = serializers.EmailField(label=('Email'), write_only=True)
    password = serializers.CharField(
        label=('Password'),
        trim_whitespace=False,
        style={'input_type': 'password'},
        write_only=True
    )


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email']=self.fields.pop('username')

    
    def get_token(cls, user):
        token = super().get_token(user)

        token['is_superuser']=user.is_superuser
        token['is_staff']=user.is_staff
        token['is_active']=user.is_active
        token['user_id']=str(user.id)
        token['services']=user.allowed_services
        token['iss']=settings.SIMPLE_JWT['ISSUER']
        token['aud']=settings.SIMPLE_JWT['AUDIENCE']

        return token
    
    def validate(self, attrs):
        authenticate_kwargs = {
            'email': attrs['email'],
            'password': attrs['password'] 
        }

        try:
            authenticate_kwargs['request']=self.context['request']
        except KeyError:
            pass

        self.user=authenticate(**authenticate_kwargs)

        if not self.user:
            raise serializers.ValidationError({"message":"Unable to login with provided credentials"}, code="authorization")
        data={}
        refresh=self.get_token(self.user)
        data['refresh']=str(refresh)
        data['access']=str(refresh.access_token)
        
        return data
    