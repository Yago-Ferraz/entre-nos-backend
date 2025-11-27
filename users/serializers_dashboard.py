from rest_framework import serializers

class ProductStatsSerializer(serializers.Serializer):
    nome = serializers.CharField()
    porcentagem_total = serializers.DecimalField(max_digits=5, decimal_places=2)

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
