from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from jwt import decode, PyJWTError
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from rest_framework.exceptions import AuthenticationFailed

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
        user=AnonymousUser()
        user.id=validated_payload.get("user_id")
        user.role=validated_payload.get('role')
        user.is_admin=validated_payload.get('is_staff')
        user.is_active=validated_payload.get('is_active')
        return user

        

