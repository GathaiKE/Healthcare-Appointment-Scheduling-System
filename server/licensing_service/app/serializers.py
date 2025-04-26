from rest_framework import serializers

from .models import License,User

class UserSerializer(serializers.ModelSerializer):
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
        user=User.objects.create(**user_data)
        license=License.objects.create(user=user, **validated_data)
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
    
    
        
        
        