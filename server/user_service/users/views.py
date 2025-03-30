from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserRegSerializer

# Create your views here.
User = get_user_model()

class RegisterUserView(APIView):
    permission_classes=[AllowAny]

    def post(self, request):
        serializer = UserRegSerializer(data=request.data)
        if(serializer.is_valid()):
            serializer.save()
            return Response({"message":"User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)