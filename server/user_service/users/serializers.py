from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
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

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","first_name", "last_name", "surname", "email", "is_staff", "is_active", "password", "phone", "date_joined"]

        def create(self, validated_data):
            user = User.objects.create_user(
                first_name= validated_data['first_name'],
                last_name = validated_data['last_name'],
                surname = validated_data['surname'],
                email=validated_data['email'],
                phone=validated_data['phone'],
                password=validated_data['password'],
                is_staff=validated_data['is_staff'],
                is_active=validated_data['is_active']
            )
            return user

class PasswordUpdateSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(label='Email', write_only=True)
    password = serializers.CharField(
        label='Password',
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
                raise serializers.ValidationError({"message":"Unable to logi in with provided credentials"}, code="authorization")
        else:
            raise serializers.ValidationError({"message":"Both email and password are required"}, code="authorization")
        
        attrs['user'] = user
        return user