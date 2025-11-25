from rest_framework import serializers
from .models import Produto
from users.serializers import BaseModelEnvelopeSerializer
from drf_spectacular.utils import extend_schema_field




class ProdutoCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'preco', 'quantidade', 'imagem']

    def create(self, validated_data):
        user = self.context['request'].user
        print(user)
        validated_data['created_by'] = user
        validated_data['updated_by'] = user
        validated_data['empresa'] = user.empresa 
        
        return super().create(validated_data)
    

    def update(self, instance, validated_data):
        validated_data['updated_by'] = self.context['request'].user
        return super().update(instance, validated_data)
    
class ProdutoResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['nome', 'descricao', 'preco', 'quantidade', 'imagem']


class ProdutoSerializer(BaseModelEnvelopeSerializer):
    results = ProdutoResultsSerializer(read_only=True, source='*')

    class Meta(BaseModelEnvelopeSerializer.Meta):
        model = Produto
    
class ProdutoMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['id', 'nome', 'preco', 'quantidade', 'imagem']



class ProdutoAnalyticsSerializer(serializers.Serializer):
    total_produtos = serializers.IntegerField()
    estoque_baixo = serializers.IntegerField()
    produto_mais_vendido = serializers.CharField(allow_null=True, allow_blank=True, required=False)

