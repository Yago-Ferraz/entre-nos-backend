from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from users.routers import router as users_router
from django.conf import settings
from django.conf.urls.static import static
from users.views import MeView
from produtos.routers import router as produtos_router
from users.views import CustomTokenObtainPairView
from pedidos.routes import router  as pedidos_router


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/auth/users/me/', MeView.as_view(), name='user-me'),
    path('api/auth/jwt/create/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Auth via Djoser
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),  # se usar JWT

    path('api/', include(users_router.urls)),
    path('api/', include(produtos_router.urls)),
    path('api/', include(pedidos_router.urls)),
    path('api/', include('moeda.urls')),
     
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 