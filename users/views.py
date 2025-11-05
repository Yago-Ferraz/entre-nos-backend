# users/views.py
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserCreateSerializer, EmpresaSerializer
import requests
from rest_framework.response import Response
from rest_framework import generics
from .serializers import CustomUserSerializer

from .models import Empresa


User = get_user_model()

class UserCreateView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer  


class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Empresa.objects.filter(user=user)
    
class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)
    

# app/auth/views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers_jwt import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    

