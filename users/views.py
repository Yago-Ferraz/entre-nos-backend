import random
from rest_framework import viewsets, permissions, generics, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response # Added this import
from django.contrib.auth import get_user_model
from .serializers import UserCreateSerializer, EmpresaSerializer, EmpresaMetaSerializer, EmpresaAvaliacaoSerializer, CustomUserSerializer, EmpresaStatsSerializer, EmpresaDashboardSerializer
from .serializers_dashboard import DashboardStatsSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from django.db.models import Sum # Added this import
from datetime import timedelta # Added this import
from .models import Empresa
from produtos.models import Produto
from moeda.models import Carteira
from django.utils import timezone
from pedidos.models import ItemPedido, Pedido
from django.db.models import Count, F
from .serializers_dashboard import WeeklyDashboardStatsSerializer


DRA_CLARA_PHRASES = [
    "A persistência é o caminho para o êxito. Continue firme!",
    "Analise seus dados, entenda seu cliente e otimize suas estratégias. O sucesso é uma construção diária.",
    "Cada desafio é uma oportunidade de inovar. Não se prenda ao passado, crie o futuro.",
    "O planejamento estratégico não é um luxo, é uma necessidade. Visualize o futuro e trabalhe para alcançá-lo.",
    "Invista em sua equipe, pois são eles que impulsionam o seu negócio. Um time motivado é um time vitorioso.",
    "A comunicação clara e eficiente é a base de qualquer negócio próspero. Fale com seus clientes e ouça-os atentamente.",
    "Mantenha-se atualizado com as tendências do mercado. A estagnação é o maior inimigo do crescimento.",
    "A qualidade do seu produto ou serviço é a sua melhor propaganda. Supere as expectativas dos seus clientes.",
    "A inovação não precisa ser disruptiva; pequenas melhorias contínuas geram grandes resultados a longo prazo.",
    "Construa relacionamentos duradouros com seus parceiros e clientes. Network é patrimônio.",
]

ALERT_PHRASES = [
    "Atenção: Queda de vendas nesta semana. Verifique seus produtos mais vendidos.",
    "Alerta: Estoque baixo para o produto X. Considere reabastecer.",
    "Notificação: Alta demanda pelo produto Y. Aumente a produção!",
    "Lembrete: Sua meta diária não foi atingida. Revise suas estratégias.",
    "Aviso: Novo concorrente no mercado. Monitore suas ações.",
]


User = get_user_model()

class UserCreateView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer  


class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Empresa.objects.filter(user=user)

    @action(detail=False, methods=['get'], serializer_class=EmpresaStatsSerializer)
    def stats(self, request):
        empresa = self.get_queryset().first()
        if not empresa:
            return Response({"error": "Empresa não encontrada."}, status=404)

        total_produtos = Produto.objects.filter(empresa=empresa).count()
        total_pedidos = Pedido.objects.filter(empresa=empresa).count()
        
        try:
            carteira = empresa.carteira
            moedas = carteira.saldo_moeda
        except Carteira.DoesNotExist:
            moedas = 0

        data = {
            'total_produtos': total_produtos,
            'total_pedidos': total_pedidos,
            'moedas': moedas,
        }
        
        serializer = self.get_serializer(data)
        return Response(serializer.data)

    @extend_schema(
        summary="Obter ou atualizar a meta da empresa",
        request=EmpresaMetaSerializer,
        responses={200: EmpresaMetaSerializer}
    )
    @action(detail=False, methods=['get', 'post'], url_path='meta')
    def meta(self, request):
        empresa = self.get_queryset().first()
        if not empresa:
            return Response({"error": "Empresa não encontrada."}, status=404)

        if request.method == 'GET':
            serializer = EmpresaMetaSerializer(empresa)
            return Response(serializer.data)

        if request.method == 'POST':
            serializer = EmpresaMetaSerializer(empresa, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)

    @extend_schema(
        summary="Obter a avaliação da empresa",
        responses={200: EmpresaAvaliacaoSerializer}
    )
    @action(detail=False, methods=['get'], url_path='avaliacao')
    def avaliacao(self, request):
        empresa = self.get_queryset().first()
        if not empresa:
            return Response({"error": "Empresa não encontrada."}, status=404)

        serializer = EmpresaAvaliacaoSerializer(empresa)
        return Response(serializer.data)

    @extend_schema(
        summary="Obter dados para o dashboard da empresa",
        responses={200: EmpresaDashboardSerializer}
    )
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        empresa = self.get_queryset().first()
        if not empresa:
            return Response({"error": "Empresa não encontrada."}, status=404)

        today = timezone.now().date()
        vendas_hoje = Pedido.objects.filter(
            empresa=empresa,
            created_at__date=today,
            status__in=['pago', 'concluido']
        ).aggregate(total=Sum('valor_total'))['total'] or 0

        data = {
            'meta': empresa.meta,
            'vendas_hoje': vendas_hoje
        }

        serializer = EmpresaDashboardSerializer(data)
        return Response(serializer.data)

    @extend_schema(
        summary="Obter dados estatísticos detalhados para o dashboard da empresa",
        responses={200: DashboardStatsSerializer}
    )
    @action(detail=False, methods=['get'], url_path='dashboard-stats')
    def dashboard_stats(self, request):
        empresa = self.get_queryset().first()
        if not empresa:
            return Response({"error": "Empresa não encontrada."}, status=404)

        # Date calculations
        today = timezone.now().date()
        # Assuming week starts on Monday (isoweekday 1)
        start_of_current_week = today - timedelta(days=today.weekday())
        end_of_current_week = start_of_current_week + timedelta(days=6)
        start_of_previous_week = start_of_current_week - timedelta(weeks=1)
        end_of_previous_week = end_of_current_week - timedelta(weeks=1)

        # 1. Vendas da Semana
        current_week_sales_queryset = Pedido.objects.filter(
            empresa=empresa,
            created_at__date__range=[start_of_current_week, end_of_current_week],
            status__in=['pago', 'concluido']
        )
        total_sales_current_week = current_week_sales_queryset.aggregate(
            total=Sum('valor_total')
        )['total'] or 0

        previous_week_sales_queryset = Pedido.objects.filter(
            empresa=empresa,
            created_at__date__range=[start_of_previous_week, end_of_previous_week],
            status__in=['pago', 'concluido']
        )
        total_sales_previous_week = previous_week_sales_queryset.aggregate(
            total=Sum('valor_total')
        )['total'] or 0

        percentual_variacao = 0
        if total_sales_previous_week > 0:
            percentual_variacao = ((total_sales_current_week - total_sales_previous_week) / total_sales_previous_week) * 100
        elif total_sales_current_week > 0:
            percentual_variacao = 100

        vendas_semana_data = {
            "total_vendas": total_sales_current_week,
            "percentual_variacao": round(percentual_variacao, 2),
        }

        # 2. Produto Mais Vendido
        # Get total quantity sold per product in the current week
        products_sold_current_week = ItemPedido.objects.filter(
            pedido__empresa=empresa,
            pedido__created_at__date__range=[start_of_current_week, end_of_current_week],
            pedido__status__in=['pago', 'concluido']
        ).values('produto__nome').annotate(
            total_quantidade_vendida=Sum('quantidade')
        ).order_by('-total_quantidade_vendida')

        produto_mais_vendido_data = {"nome": "Nenhum", "porcentagem_total": 0}
        
        if products_sold_current_week.exists():
            most_sold_product = products_sold_current_week.first()
            total_all_products_quantity = ItemPedido.objects.filter(
                pedido__empresa=empresa,
                pedido__created_at__date__range=[start_of_current_week, end_of_current_week],
                pedido__status__in=['pago', 'concluido']
            ).aggregate(total_q=Sum('quantidade'))['total_q'] or 0

            if total_all_products_quantity > 0:
                porcentagem = (most_sold_product['total_quantidade_vendida'] / total_all_products_quantity) * 100
                produto_mais_vendido_data = {
                    "nome": most_sold_product['produto__nome'],
                    "porcentagem_total": round(porcentagem, 2),
                }

        # 3. Média Diária da Semana
        # Sum of valor_total for the current week (already calculated as total_sales_current_week)
        # Number of days in the current week for which there were sales
        distinct_sale_days = Pedido.objects.filter(
            empresa=empresa,
            created_at__date__range=[start_of_current_week, end_of_current_week],
            status__in=['pago', 'concluido']
        ).dates('created_at', 'day').count()
        
        # Consider all 7 days of the week for the average, even if no sales on some days
        days_in_week = 7 
        
        media_diaria = 0
        if days_in_week > 0:
            media_diaria = total_sales_current_week / days_in_week

        media_diaria_semana_data = {
            "valor_medio_diario": round(media_diaria, 2),
            "periodo_referencia": f"{start_of_current_week.strftime('%d/%m')} - {end_of_current_week.strftime('%d/%m')}",
        }

        dashboard_data = {
            "vendas_semana": vendas_semana_data,
            "produto_mais_vendido": produto_mais_vendido_data,
            "media_diaria_semana": media_diaria_semana_data,
        }

        serializer = DashboardStatsSerializer(dashboard_data)
        return Response(serializer.data)

    @extend_schema(
        summary="Obter resumo semanal do dashboard da empresa",
        responses={200: WeeklyDashboardStatsSerializer}
    )
    @action(detail=False, methods=['get'], url_path='weekly-dashboard-summary')
    def weekly_dashboard_summary(self, request):
        empresa = self.get_queryset().first()
        if not empresa:
            return Response({"error": "Empresa não encontrada."}, status=404)

        # Date calculations
        today = timezone.now().date()
        start_of_current_week = today - timedelta(days=today.weekday())
        end_of_current_week = start_of_current_week + timedelta(days=6)

        # 1. Weekly Sales Total
        current_week_sales_queryset = Pedido.objects.filter(
            empresa=empresa,
            created_at__date__range=[start_of_current_week, end_of_current_week],
            status__in=['pago', 'concluido']
        )
        total_sales_current_week = current_week_sales_queryset.aggregate(
            total=Sum('valor_total')
        )['total'] or 0

        # 2. Best-Selling Product of the Week
        products_sold_current_week = ItemPedido.objects.filter(
            pedido__empresa=empresa,
            pedido__created_at__date__range=[start_of_current_week, end_of_current_week],
            pedido__status__in=['pago', 'concluido']
        ).values('produto__nome').annotate(
            total_quantidade_vendida=Sum('quantidade')
        ).order_by('-total_quantidade_vendida')

        produto_mais_vendido_data = {"nome": "Nenhum", "porcentagem_total": 0}

        if products_sold_current_week.exists():
            most_sold_product = products_sold_current_week.first()
            total_all_products_quantity = ItemPedido.objects.filter(
                pedido__empresa=empresa,
                pedido__created_at__date__range=[start_of_current_week, end_of_current_week],
                pedido__status__in=['pago', 'concluido']
            ).aggregate(total_q=Sum('quantidade'))['total_q'] or 0

            if total_all_products_quantity > 0:
                produto_mais_vendido_data = {
                    "nome": most_sold_product['produto__nome'],
        
                }

        # 3. Weekly Sales Target
        weekly_sales_target = empresa.meta * 7

        # 4. Random "Dra. Clara" Phrases
        random_dra_clara_phrases = random.sample(DRA_CLARA_PHRASES, min(3, len(DRA_CLARA_PHRASES)))

        # 5. Random "Intelligent Alert" Phrases
        random_alert_phrases = random.sample(ALERT_PHRASES, min(2, len(ALERT_PHRASES)))

        # 6. Daily Sales Value (Monday to Friday)
        sales_by_day = {}
        day_names = {
            1: 'segunda', 2: 'terca', 3: 'quarta', 4: 'quinta', 5: 'sexta'
        }
        for i in range(1, 6): # Monday to Friday
            day = start_of_current_week + timedelta(days=i - 1)
            daily_sales_total = Pedido.objects.filter(
                empresa=empresa,
                created_at__date=day,
                status__in=['pago', 'concluido']
            ).aggregate(total=Sum('valor_total'))['total'] or 0
            sales_by_day[day_names[i]] = daily_sales_total

        # Prepare the response data
        response_data = {
            "total_venda_semana": total_sales_current_week,
            "produto_mais_vendido_semana": produto_mais_vendido_data,
            "meta_diaria": empresa.meta, # Added this line
            "meta_semanal": weekly_sales_target,
            "frases_dra_clara": random_dra_clara_phrases,
            "alertas_inteligentes": random_alert_phrases,
            "vendas_por_dia_semana": sales_by_day,
        }
        
        serializer = WeeklyDashboardStatsSerializer(response_data)
        return Response(serializer.data)
    
class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)

class MotivacionalView(APIView):
    @extend_schema(        summary="Obter frases motivacionais aleatórias",
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response={"phrase": "string"},
                examples=[
                    OpenApiExample(
                        'Frase Motivacional Exemplo',
                        value={"phrase": "Acredite em você. Você é mais forte do que pensa!"}
                    ),
                ]
            )
        }
    )
    def get(self, request):
        phrases = [
            "Acredite em você. Você é mais forte do que pensa!",
            "O único lugar onde o sucesso vem antes do trabalho é no dicionário.",
            "Não espere por oportunidades, crie-as.",
            "Seus sonhos não têm data de validade. Respire fundo e tente novamente.",
            "O futuro pertence àqueles que acreditam na beleza de seus sonhos.",
            "A persistência realiza o impossível.",
            "Grandes coisas nunca vêm de zonas de conforto.",
            "Cada passo que você dá te leva para mais perto do seu objetivo.",
            "Comece onde você está. Use o que você tem. Faça o que você pode.",
            "A vida é 10% o que acontece com você e 90% como você reage a isso."
        ]
        random_phrase = random.choice(phrases)
        return Response({"phrase": random_phrase}, status=status.HTTP_200_OK)
    

# app/auth/views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers_jwt import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

