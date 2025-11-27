from django.urls import path
from .views import CarteiraEmpresaView, TransacaoListView

urlpatterns = [
    path('carteira/', CarteiraEmpresaView.as_view(), name='carteira-empresa'),
    path('carteira/transacoes/', TransacaoListView.as_view(), name='transacao-list'),
]