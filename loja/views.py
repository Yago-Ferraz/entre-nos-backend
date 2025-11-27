from rest_framework import generics, permissions
from users.models import Empresa
from .serializers import EmpresaLojaDetailSerializer, ProdutoComUpsellSerializer, ProdutoLojaSerializer
from rest_framework.exceptions import NotFound
from produtos.models import Produto


class EmpresaLojaDetailView(generics.RetrieveAPIView):
    queryset = Empresa.objects.all().select_related('user').prefetch_related(
        'fotos',
        'produtos'
    )
    serializer_class = EmpresaLojaDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return self.request.user.empresa
        except Empresa.DoesNotExist:
            raise NotFound("Empresa não encontrada para o usuário autenticado.")


class ProdutoLojaDetailView(generics.RetrieveAPIView):
    queryset = Produto.objects.all()
    serializer_class = ProdutoComUpsellSerializer
    permission_classes = [permissions.AllowAny]