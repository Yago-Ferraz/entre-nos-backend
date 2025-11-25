from django.db import models
from users.models import User, BaseModel
from produtos.models import Produto
from users.models import Empresa


class Pedido(BaseModel):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("processando", "Processando"),
        ("pago", "Pago"),
        ("cancelado", "Cancelado"),
        ("concluido", "Concluído"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pendente")
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def atualizar_total(self):
        valor_total = sum(item.subtotal() for item in self.itens.all())
        self.valor_total = valor_total
        self.save()

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario}"




class ItemPedido(BaseModel):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.quantidade * self.preco_unitario

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"

    def save(self, *args, **kwargs):
        # Preenche preço automaticamente
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco

        # Se o pedido ainda não tem empresa, define automaticamente
        if self.pedido.empresa is None:
            self.pedido.empresa = self.produto.empresa
            self.pedido.save()

        # Se tentar adicionar item de outra empresa → ERRO
        if self.pedido.empresa != self.produto.empresa:
            raise ValueError("Todos os itens do pedido devem ser da mesma empresa.")

        super().save(*args, **kwargs)