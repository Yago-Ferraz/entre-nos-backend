from rest_framework import serializers
from .models import Pedido, ItemPedido
from produtos.models import Produto

class ItemPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPedido
        fields = ["id", "produto", "quantidade", "preco_unitario", "subtotal"]
        read_only_fields = ["id", "preco_unitario", "subtotal"]

    subtotal = serializers.SerializerMethodField()

    def get_subtotal(self, obj):
        return obj.subtotal()


class PedidoSerializer(serializers.ModelSerializer):
    itens = ItemPedidoSerializer(many=True)

    class Meta:
        model = Pedido
        fields = ["id", "usuario", "status", "valor_total", "itens"]
        read_only_fields = ["id", "valor_total", "status"]

    def create(self, validated_data):
        itens_data = validated_data.pop("itens")
        pedido = Pedido.objects.create(**validated_data)

        valor_total = 0

        for item_data in itens_data:
            produto = Produto.objects.get(id=item_data["produto"].id)

            preco_unitario = produto.preco
            quantidade = item_data["quantidade"]

            # cria item
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=quantidade,
                preco_unitario=preco_unitario
            )

            valor_total += quantidade * preco_unitario

            # atualizar estoque
            produto.quantidade -= quantidade
            produto.save()

        pedido.valor_total = valor_total
        pedido.save()

        return pedido
