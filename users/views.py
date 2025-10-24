# users/views.py
from rest_framework import viewsets, mixins
from django.contrib.auth import get_user_model
from .serializers import UsersSerializer
import requests
from rest_framework.response import Response
from .models import Foto

User = get_user_model()

class UserViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    
    def create(self, request, *args, **kwargs):
        print('ta chegando aqui', request.data)

        # Pega fotos e logo do request.FILES
        fotos_files = request.FILES.getlist('fotos')
        logo_file = request.FILES.get('logo')

        # Passa o contexto para o serializer (necessário para alguns casos)
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        # Cria o usuário sem os arquivos
        user = serializer.save()

        # Salva logo separadamente
        if logo_file:
            user.logo = logo_file
            user.save()

        # Salva fotos
        for f in fotos_files:
            Foto.objects.create(user=user, imagem=f)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)