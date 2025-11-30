# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Empresa, FotoEmpresa
from .models import FotoEmpresa
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from djoser.serializers import TokenCreateSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model



User = get_user_model()

class FotoEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FotoEmpresa
        fields = ['id', 'imagem']

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'usertype', 'password']
        

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user
    

class EmpresaSerializer(serializers.ModelSerializer):
    fotos = FotoEmpresaSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    # Para upload de fotos junto com a empresa
    fotos_upload = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    ) 

    class Meta:
        model = Empresa
        fields = ['id', 'user', 'categoria', 'descricao', 'logo', 'fotos', 'fotos_upload']

    def create(self, validated_data):
        fotos_upload = validated_data.pop('fotos_upload', [])
        empresa = Empresa.objects.create(**validated_data)

        # Criar objetos FotoEmpresa
        for foto in fotos_upload:
            FotoEmpresa.objects.create(empresa=empresa, imagem=foto)

        return empresa

    def update(self, instance, validated_data):
        fotos_upload = validated_data.pop('fotos_upload', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        for foto in fotos_upload:
            FotoEmpresa.objects.create(empresa=instance, imagem=foto)

        return instance
    

class EmpresaStatsSerializer(serializers.Serializer):
    total_produtos = serializers.IntegerField(read_only=True)
    total_pedidos = serializers.IntegerField(read_only=True)
    moedas = serializers.IntegerField(read_only=True)


class EmpresaMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['meta']

class EmpresaAvaliacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['avaliacao']


class EmpresaDashboardSerializer(serializers.Serializer):
    meta = serializers.IntegerField()
    vendas_hoje = serializers.DecimalField(max_digits=12, decimal_places=2)


class CustomUserSerializer(serializers.ModelSerializer):
    empresa = EmpresaSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'usertype', 'empresa']


class MotivacionalSerializer(serializers.Serializer):
    phrase = serializers.CharField(help_text="Frase motivacional aleatória")


from rest_framework import serializers

class BaseModelEnvelopeSerializer(serializers.ModelSerializer):
    criador_nome = serializers.SerializerMethodField()
    created_by_nome = serializers.SerializerMethodField()
    updated_by_nome = serializers.SerializerMethodField()
    results = serializers.SerializerMethodField()

    class Meta:
        model = None  # definido no serializer filho
        fields = [
            'id', 'criador_nome', 'created_at', 'updated_at',
            'created_by_nome', 'updated_by_nome', 'results'
        ]
        read_only_fields = fields

    def get_criador_nome(self, obj):
        return getattr(obj.created_by, 'username', None)

    def get_created_by_nome(self, obj):
        return getattr(obj.created_by, 'username', None)

    def get_updated_by_nome(self, obj):
        return getattr(obj.updated_by, 'username', None)

    def get_results(self, obj):
        base_fields = {'id', 'created_at', 'updated_at', 'created_by', 'updated_by'}
        result = {}
        for f in obj._meta.get_fields():
            if f.name in base_fields:
                continue
            # evita relações many-to-many ou reverse
            if f.many_to_many or f.one_to_many:
                continue
            value = getattr(obj, f.name)
            # se for ImageField ou FileField, retorna a URL
            if isinstance(f, (ImageField, FileField)) and value:
                value = value.url
            result[f.name] = value
        return result

    # Preenche automaticamente created_by e updated_by
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user
        validated_data['updated_by'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        validated_data['updated_by'] = user
        return super().update(instance, validated_data)
    

