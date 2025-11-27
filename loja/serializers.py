from rest_framework import serializers
from users.models import User, Empresa, FotoEmpresa
from produtos.models import Produto

class UserOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'email', 'phone']

class FotoEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FotoEmpresa
        fields = ['imagem']

class ProdutoLojaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        # Assuming 'todas as caracteristicas do produto' means all fields.
        # Exclude 'empresa' as it will be nested.
        exclude = ['empresa']

class EmpresaLojaDetailSerializer(serializers.ModelSerializer):
    user = UserOwnerSerializer(read_only=True)
    fotos = FotoEmpresaSerializer(many=True, read_only=True)
    produtos = ProdutoLojaSerializer(many=True, read_only=True)

    class Meta:
        model = Empresa
        fields = ['id', 'descricao', 'avaliacao', 'logo', 'user', 'fotos', 'produtos']


class ProdutoComUpsellSerializer(serializers.ModelSerializer):
    upsell_produtos = ProdutoLojaSerializer(many=True, read_only=True)

    class Meta:
        model = Produto
        fields = [
            'id', 
            'created_at', 
            'updated_at', 
            'created_by', 
            'updated_by', 
            'imagem', 
            'nome', 
            'descricao', 
            'preco', 
            'quantidade',
            'upsell_produtos'
        ]
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        empresa_principal = instance.empresa
        if not empresa_principal:
            representation['upsell_produtos'] = []
            return representation

        upsell_produtos = Produto.objects.filter(
            empresa=empresa_principal
        ).exclude(
            id=instance.id
        ).order_by('?')[:5]
        
        representation['upsell_produtos'] = ProdutoLojaSerializer(upsell_produtos, many=True).data
        return representation

