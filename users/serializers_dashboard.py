from rest_framework import serializers

class ProductStatsSerializer(serializers.Serializer):
    nome = serializers.CharField()
    porcentagem_total = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)

class WeeklySalesSerializer(serializers.Serializer):
    total_vendas = serializers.IntegerField()
    percentual_variacao = serializers.DecimalField(max_digits=5, decimal_places=2)

class DailyAverageSerializer(serializers.Serializer):
    valor_medio_diario = serializers.DecimalField(max_digits=10, decimal_places=2)
    periodo_referencia = serializers.CharField()

class DashboardStatsSerializer(serializers.Serializer):
    vendas_semana = WeeklySalesSerializer()
    produto_mais_vendido = ProductStatsSerializer()
    media_diaria_semana = DailyAverageSerializer()

class WeeklyDashboardStatsSerializer(serializers.Serializer):
    total_venda_semana = serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True)
    produto_mais_vendido_semana = ProductStatsSerializer()
    meta_diaria = serializers.IntegerField() # Added this line
    meta_semanal = serializers.IntegerField()
    frases_dra_clara = serializers.ListField(child=serializers.CharField())
    alertas_inteligentes = serializers.ListField(child=serializers.CharField())
    vendas_por_dia_semana = serializers.DictField(child=serializers.DecimalField(max_digits=12, decimal_places=2, allow_null=True))

