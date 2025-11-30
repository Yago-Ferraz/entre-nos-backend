from rest_framework import serializers
from .models import Pedido, ItemPedido
from produtos.models import Produto
from produtos.serializer import ProdutoSerializer
from users.models import User


class ItemPedidoSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ItemPedido
        fields = ["id", "produto", "quantidade", "preco_unitario", "subtotal"]
        read_only_fields = ["id", "preco_unitario", "subtotal"]

    def get_subtotal(self, obj):
        return obj.subtotal()


class PedidoSerializer(serializers.ModelSerializer):
    itens = ItemPedidoSerializer(many=True)
    comprador = serializers.CharField(source='usuario.name', read_only=True)
    usuario = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Pedido
        fields = ["id", "comprador", "usuario", "empresa", "status", "valor_total", "itens", "descricao"]
        read_only_fields = ["id", "valor_total", "status", "empresa"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('usuario', None)
        return representation

    def create(self, validated_data):
        itens_data = validated_data.pop("itens")
        pedido = Pedido.objects.create(**validated_data)

        valor_total = 0
        empresa_do_pedido = None

        for item_data in itens_data:

            # Produto real do banco
            produto = Produto.objects.get(id=item_data["produto"].id)

            # Verifica empresa do produto
            produto_empresa = produto.created_by.empresa if hasattr(produto.created_by, "empresa") else None
            
            if produto_empresa is None:
                raise serializers.ValidationError(
                    f"O produto '{produto.nome}' não possui empresa vinculada."
                )

            # Configura empresa do pedido automaticamente
            if empresa_do_pedido is None:
                empresa_do_pedido = produto_empresa
                pedido.empresa = empresa_do_pedido
                pedido.save()
            else:
                if empresa_do_pedido != produto_empresa:
                    raise serializers.ValidationError(
                        "Todos os produtos do pedido devem ser da mesma empresa."
                    )

            quantidade = item_data["quantidade"]
            preco_unitario = produto.preco

            # Criar item
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=quantidade,
                preco_unitario=preco_unitario
            )

            # Atualiza estoque
            produto.quantidade -= quantidade
            if produto.quantidade < 0:
                raise serializers.ValidationError(
                    f"Estoque insuficiente para o produto {produto.nome}."
                )
            produto.save()

            valor_total += quantidade * preco_unitario

        pedido.valor_total = valor_total
        pedido.save()

        return pedido


class PedidoUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ["status", "descricao"]
