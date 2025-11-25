from rest_framework import viewsets
from .models import Pedido
from .serializers import PedidoSerializer

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

    def get_queryset(self):
        usuario = self.request.user
        return Pedido.objects.filter(usuario=usuario)
