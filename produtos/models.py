from django.db import models
from users.models import BaseModel
from users.models import Empresa

class Produto(BaseModel):
    imagem = models.ImageField(upload_to='produtos/')
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField()
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="produtos")

    def __str__(self):
        return self.nome