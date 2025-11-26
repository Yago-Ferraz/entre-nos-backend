from rest_framework.routers import DefaultRouter
from pedidos.views import PedidoViewSet

router = DefaultRouter()
router.register(r'pedidos', PedidoViewSet, basename='pedidos')

urlpatterns = router.urls
