from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Produto
from .serializer import ProdutoSerializer, ProdutoCreateUpdateSerializer


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