import json
from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from .serializers import UserSerializer, AdminSerializer, PasswordUpdateSerializer, AuthTokenSerializer
from .permissions import IsOwnerOrAdmin

User = get_user_model()

class RegisterUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

class AuthenticateView(APIView):
    serializer_class= AuthTokenSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'surname': user.surname,
                'email': user.surname,
                'is_active': user.is_active,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff,
                'date_joined': user.date_joined,
                'last_login': user.last_login
            },
        })

class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = AdminSerializer
    permission_classes = [IsAdminUser]
    throttle_classes = [UserRateThrottle]


    def get_serializer_class(self):
        if self.request.user.is_staff:
            return AdminSerializer
        return UserSerializer
    
    def perform_destroy(self, instance):
        instance.delete()

class UserDetailVeiew(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    throttle_classes = [UserRateThrottle]


    def get_serializer_class(self):
        if self.request.user.is_staff:
            return AdminSerializer
        return UserSerializer
    
    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

class PasswordResetView(generics.UpdateAPIView):
    serializer_class = PasswordUpdateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    throttle_classes = [UserRateThrottle]


    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.data.get('old_password')):
                return Response({"old_password": ['wrong_password']}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.data.get(('new_password')))
            user.save()
            return Response({"status": "password updated"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
