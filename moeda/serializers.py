from rest_framework import serializers
from moeda.models import Carteira, Transacao

class CarteiraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carteira
        fields = ['saldo_dinheiro', 'saldo_moeda', 'atualizado_em']

class TransacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transacao
        fields = '__all__'
        read_only_fields = ['carteira', 'valor_movimentado', 'created_at', 'updated_at']

class TransacaoInputSerializer(serializers.Serializer):
    valor = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=0.01)
    tipo_ativo = serializers.ChoiceField(choices=Transacao.OPCOES_ATIVO)
    tipo_operacao = serializers.ChoiceField(choices=Transacao.OPCOES_OPERACAO)
    descricao = serializers.CharField(max_length=255, required=False, allow_blank=True)
