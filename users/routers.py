from rest_framework.routers import DefaultRouter
from .views import UserCreateView, EmpresaViewSet, MeView

router = DefaultRouter()
router.register(r'users', UserCreateView, basename='user')
router.register(r'empresa', EmpresaViewSet, basename='empresa')


urlpatterns = router.urls 