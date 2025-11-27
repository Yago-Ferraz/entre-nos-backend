from django.urls import path
from .views import EmpresaLojaDetailView, ProdutoLojaDetailView

urlpatterns = [
    path('empresa/me/', EmpresaLojaDetailView.as_view(), name='empresa-detail-loja-me'),
    path('produtos/<int:pk>/', ProdutoLojaDetailView.as_view(), name='produto-detail-loja'),
]
