from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from jwt import decode, PyJWTError
from django.contrib.auth.models import AbstractBaseUser
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


class ServiceUser(AbstractBaseUser):
    class Meta:
        managed=False

    def __init__(self, user_id, role, is_staff, is_superuser, is_active):
        self.id=user_id
        self.role=role
        self.is_staff=is_staff
        self.is_superuser=is_superuser
        self.is_active=is_active

        @property
        def is_authenticated(self):
            return True

        @property
        def is_anonymous(self):
            return False
        
        USERNAME_FIELD='id'
        REQUIRED_FIELDS=[]

class JWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header=self.get_header(request)
        if header is None:
            return None
        
        raw_token=self.get_raw_token(header)
        payload=self.get_unvalidated_token(raw_token)

        issuer=payload.get('iss')
        audience=payload.get('aud')

        public_key=settings.PUBLIC_KEYS.get(issuer)


        if not public_key:
            raise AuthenticationFailed("Invalid issuer", code='invalid_issuer')
        
        if settings.SIMPLE_JWT['AUDIENCE'] not in audience:
            raise AuthenticationFailed("Invalid Audience", code='invalid_audience')

        try:

            validated_payload=self.validate_token(raw_token, public_key)
            user=self.get_user(validated_payload)
            return (user, validated_payload)
        except PyJWTError as e:
            raise AuthenticationFailed("Invalid token structure") from e
        
    def get_unvalidated_token(self, raw_token):
        return decode(raw_token, options={'verify_signature': False})
    
    def get_validated_token(self, raw_token, key):
        return super().get_validated_token(raw_token, key)

    def validate_token(self, raw_token, public_key):
        try:
            return decode(
                raw_token,
                key=public_key,
                algorithms=[settings.SIMPLE_JWT['ALGORITHM']],
                audience=settings.SIMPLE_JWT['AUDIENCE'],
                issuer=list(settings.SIMPLE_JWT['ISSUER']),
                options={'require':['exp', 'iat', 'iss', 'aud']}
            )
        except PyJWTError as e:
            raise InvalidToken(f"Invalid signature {str(e)}") from e
    
    def get_user(self, validated_payload):
        return ServiceUser(
            user_id=validated_payload.get("user_id"),
            role=validated_payload.get('role'),
            is_staff=validated_payload.get('is_staff'),
            is_active=validated_payload.get('is_active'),
            is_superuser=validated_payload.get('is_superuser')
        )

        

