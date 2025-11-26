from django.db import models
from users.models import User, BaseModel, Empresa
from django.db import transaction
from django.core.exceptions import ValidationError

class Carteira(models.Model):
    """
    Representa o estado atual dos saldos da empresa.
    """
    empresa = models.OneToOneField(Empresa, on_delete=models.CASCADE, related_name='carteira')
    saldo_dinheiro = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    saldo_moeda = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carteira de {self.empresa.user.name} - R$ {self.saldo_dinheiro} | Moedas: {self.saldo_moeda}"
 
    @transaction.atomic
    def registrar_operacao(self, valor, tipo_ativo, tipo_operacao, descricao="", user=None):
        """
        Método atômico para criar log e atualizar saldo simultaneamente.
        Se uma das partes falhar, nada é salvo no banco (Rollback).
        """
        
        # 1. Determina se é Entrada ou Saída baseado no tipo de operação
        # Define multiplicador: 1 para entrada, -1 para saída
        if tipo_operacao in Transacao.get_tipos_entrada():
            multiplicador = 1
        elif tipo_operacao in Transacao.get_tipos_saida():
            multiplicador = -1
        else:
            raise ValidationError("Tipo de operação inválido.")

        valor_final = valor * multiplicador

        # 2. Verificação de Saldo (apenas para saídas)
        if multiplicador == -1:
            if tipo_ativo == Transacao.ATIVO_DINHEIRO and self.saldo_dinheiro < valor:
                raise ValidationError("Saldo insuficiente em Dinheiro.")
            elif tipo_ativo == Transacao.ATIVO_MOEDA and self.saldo_moeda < valor:
                raise ValidationError("Saldo insuficiente em Moedas.")

        # 3. Cria o Log (Transacao)
        Transacao.objects.create(
            carteira=self,
            valor=valor, # Salvamos o valor absoluto no log
            valor_movimentado=valor_final, # Valor com sinal (+ ou -) para cálculos
            tipo_ativo=tipo_ativo,
            tipo_operacao=tipo_operacao,
            descricao=descricao,
            created_by=user,
            updated_by=user
        )

        # 4. Atualiza o Saldo da Carteira
        if tipo_ativo == Transacao.ATIVO_DINHEIRO:
            self.saldo_dinheiro += valor_final
        else:
            self.saldo_moeda += valor_final
        
        self.save()

class Transacao(BaseModel):
    """
    Log histórico de todas as operações (Ledger).
    Nunca deve ser alterado ou deletado, apenas criado.
    """
    
    # Opções de Ativos
    ATIVO_DINHEIRO = 'BRL'
    ATIVO_MOEDA = 'COIN'
    
    OPCOES_ATIVO = [
        (ATIVO_DINHEIRO, 'Dinheiro Real (R$)'),
        (ATIVO_MOEDA, 'Moeda do App'),
    ]

    # Tipos de Operação
    OP_DEPOSITO = 'DEPOSITO'      # Aumenta Dinheiro
    OP_COMPRA_MOEDA = 'COMPRA_COIN' # Diminui Dinheiro, Aumenta Moeda (Requer 2 transações ou lógica composta)
    OP_GASTO_MOEDA = 'GASTO'      # Diminui Moeda
    OP_BONUS = 'BONUS'            # Aumenta Moeda (Recompensa)
    OP_SAQUE = 'SAQUE'            # Diminui Dinheiro
    OP_ESTORNO = 'ESTORNO'        # Aumenta Dinheiro ou Moeda

    OPCOES_OPERACAO = [
        (OP_DEPOSITO, 'Depósito'),
        (OP_COMPRA_MOEDA, 'Compra de Moeda'),
        (OP_GASTO_MOEDA, 'Gasto de Moeda/Serviço'),
        (OP_BONUS, 'Bônus/Recompensa'),
        (OP_SAQUE, 'Saque'),
        (OP_ESTORNO, 'Estorno'),
    ]

    carteira = models.ForeignKey(Carteira, on_delete=models.PROTECT, related_name='transacoes')
    tipo_ativo = models.CharField(max_length=4, choices=OPCOES_ATIVO)
    tipo_operacao = models.CharField(max_length=20, choices=OPCOES_OPERACAO)
    
    # Valor absoluto da transação (ex: 50.00)
    valor = models.DecimalField(max_digits=14, decimal_places=2)
    
    # Valor com sinal para facilitar somas no banco (ex: -50.00 ou +50.00)
    valor_movimentado = models.DecimalField(max_digits=14, decimal_places=2)
    
    descricao = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Transação"
        verbose_name_plural = "Transações"
        indexes = [
            models.Index(fields=['carteira', '-created_at']),
        ]

    def __str__(self):
        sinal = "+" if self.valor_movimentado >= 0 else "-"
        return f"{self.get_tipo_operacao_display()}: {sinal} {self.valor} ({self.tipo_ativo})"

    @staticmethod
    def get_tipos_entrada():
        return [Transacao.OP_DEPOSITO, Transacao.OP_BONUS, Transacao.OP_ESTORNO]

    @staticmethod
    def get_tipos_saida():
        return [Transacao.OP_SAQUE, Transacao.OP_GASTO_MOEDA, Transacao.OP_COMPRA_MOEDA]