from rest_framework_simplejwt.authentication import JWTAuthentication
from jwt import InvalidAudienceError
from django.conf import settings 
from rest_framework.exceptions import AuthenticationFailed

class Authenticate(JWTAuthentication):
    def get_validated_token(self, raw_token):
        token=super().get_validated_token(raw_token)

        if settings.SIMPLE_JWT['AUDIENCE'] not in token.get('aud',[]):
            raise InvalidAudienceError("Invalid audience")
        
        if token.get('iss') != settings.SIMPLE_JWT['ISSUER']:
            raise AuthenticationFailed('Invalid Token Issuer', code='invalid_issuer')
        
        return token