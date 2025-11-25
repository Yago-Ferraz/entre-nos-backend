from rest_framework import serializers
from .models import Pedido, ItemPedido
from produtos.models import Produto


class ItemPedidoSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ItemPedido
        fields = ["id", "produto", "quantidade", "preco_unitario", "subtotal"]
        read_only_fields = ["id", "preco_unitario", "subtotal"]

    def get_subtotal(self, obj):
        return obj.subtotal()


class PedidoSerializer(serializers.ModelSerializer):
    itens = ItemPedidoSerializer(many=True)

    class Meta:
        model = Pedido
        fields = ["id", "usuario", "empresa", "status", "valor_total", "itens"]
        read_only_fields = ["id", "valor_total", "status", "empresa"]

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
