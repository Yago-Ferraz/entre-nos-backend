from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Pedido
from .serializers import PedidoSerializer, PedidoUpdateStatusSerializer

class PedidoViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

    def get_queryset(self):
        usuario = self.request.user
        empresa = usuario.empresa
        a = Pedido.objects.filter(empresa=empresa)
        return a

    @extend_schema(
        request=PedidoUpdateStatusSerializer,
        responses={200: PedidoUpdateStatusSerializer, 400: None},
        description="Atualiza o status e a descrição de um pedido específico."
    )
    @action(detail=True, methods=['patch'])
    def atualizar_status_descricao(self, request, pk=None):
        pedido = self.get_object()
        serializer = PedidoUpdateStatusSerializer(pedido, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
