from rest_framework import serializers
from django.utils import timezone
from django.core.validators import FileExtensionValidator

from .models import License,User

class UserSerializer(serializers.ModelSerializer):
    face_img=serializers.ImageField(allow_empty_file=False, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])], required=False)
    practicing_certificate=serializers.FileField(allow_empty_file=False, validators=[FileExtensionValidator(allowed_extensions=['pdf'])], required=False)
    identity_card=serializers.FileField(allow_empty_file=False, validators=[FileExtensionValidator(allowed_extensions=['pdf'])], required=False)
    
    class Meta:
        model=User
        fields=['id','user_id','face_img','practicing_certificate','identity_card','valid_practicing_certificate','valid_identity_card','valid_face_img','created_at','updated_at']
        read_only_fields=['id','valid_practicing_certificate','valid_identity_card','valid_face_img','created_at','updated_at']

class LicenseSerializer(serializers.ModelSerializer):
    user=UserSerializer(required=True)
    expiration_date=serializers.DateTimeField(required=False)

    class Meta:
        model=License
        fields=['id', 'user', 'status', 'expiration_date', 'practicing_certificate_is_valid', 'identity_card_is_valid','face_verification', 'is_valid', 'created_at','updated_at']
        read_only_fields=['practicing_certificate_is_valid', 'identity_card_is_valid','face_verification', 'is_valid','created_at','updated_at', 'id']
        extra_kwargs={
            'status':{
                'required':False
            }
        }

    def create(self, validated_data):
        user_data=validated_data.pop('user')
        if not user_data.get('user_id'):
            raise serializers.ValidationError("User data is required.")
        
        face_img=user_data.get('face_img', None)
        practicing_certificate=user_data.get('practicing_certificate', None)
        identity_card=user_data.get('identity_card', None)
        user=User.objects.create(user_id=user_data.get('user_id'), face_img=face_img, practicing_certificate=practicing_certificate, identity_card=identity_card)
        expiration_date=timezone.now() + timezone.timedelta(days=3650)
        status=License.LicenseStatus.PENDING
        license=License.objects.create(user=user, expiration_date=expiration_date, status=status)
        return license
    
    def update(self, instance, validated_data):
        user_data=validated_data.pop('user', None)
        if user_data:
            for attr, value in user_data.items():
                if attr in ['user_id','valid_practicing_certificate', 'valid_identity_card', 'valid_face_img']:
                    pass
                else:
                    setattr(instance.user, attr, value)
            instance.user.save()
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    
        
        
        