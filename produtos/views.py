from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Produto
from .serializer import (
    ProdutoSerializer,
    ProdutoCreateUpdateSerializer,
    ProdutoAnalyticsSerializer,
    ProdutoMinimalSerializer
)
from rest_framework.decorators import action

class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    



class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        # POST/PUT/PATCH usam o serializer que seta created_by / updated_by
        if self.action in ['create', 'update', 'partial_update']:
            return ProdutoCreateUpdateSerializer
        # GET/list/retrieve usam o envelope
        return ProdutoSerializer

    # Sobrescreve o list para incluir envelope
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = ProdutoSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        user = request.user

        produtos = Produto.objects.filter(created_by=user)


        # 2. Estoque baixo
        estoque_baixo_qs = produtos.filter(quantidade__lt=5)
        estoque_baixo = ProdutoMinimalSerializer(estoque_baixo_qs, many=True).data

        # 3. Produto mais vendido → ainda não existe lógica de vendas
        produto_mais_vendido = None

        # Monta o payload
        payload = {
            "total_produtos": produtos.count(),
            "estoque_baixo": estoque_baixo_qs.count(),
            "produto_mais_vendido": None,
        }

        serializer = ProdutoAnalyticsSerializer(payload)
        return Response(serializer.data)