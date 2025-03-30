from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "surname", "email", "password", "phone"]

        def create(self, validated_data):
            user = User.objects.create_user(
                first_name = validated_data['first_name'],
                last_name = validated_data["first_name"],
                surname = validated_data["surname"],
                email = validated_data["email"],
                phone = validated_data["phone"],
                password = validated_data["password"]
            )
            return user