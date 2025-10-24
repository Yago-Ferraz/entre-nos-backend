# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer
from djoser.serializers import UserCreateSerializer
from .models import Foto

User = get_user_model()

class FotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'fotos']

class UsersSerializer(UserCreateSerializer):
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)
    fotos = serializers.ListField(
        child=serializers.ImageField(), required=False
    )
    logo = serializers.ImageField(required=False)
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'name',
            'password',
            'usertype',
            'phone',
            'cnpj',
            'categoria',
            'descricao',
            'logo',
            'fotos',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        request = self.context.get('request')

        # Remove arquivos de validated_data
        logo_file = request.FILES.get('logo') if request else None
        fotos_files = request.FILES.getlist('fotos') if request else []

        validated_data.pop('fotos', None)
        validated_data.pop('logo', None)

        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)

        # Salva logo
        if logo_file:
            user.logo = logo_file
            user.save()

        # Salva fotos
        for f in fotos_files:
            Foto.objects.create(user=user, imagem=f)

        return user
    
