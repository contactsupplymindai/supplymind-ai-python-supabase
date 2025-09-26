"""
URL Configuration for SupplyMind AI Backend

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Health check endpoint
def health_check(request):
    """Simple health check endpoint for load balancers and monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'supplymind-ai-backend',
        'version': '1.0.0'
    })

# API root endpoint
def api_root(request):
    """API root endpoint with service information"""
    return JsonResponse({
        'message': 'Welcome to SupplyMind AI Backend API',
        'version': '1.0.0',
        'documentation': {
            'swagger': '/api/docs/',
            'redoc': '/api/redoc/',
            'openapi_schema': '/api/schema/'
        },
        'endpoints': {
            'authentication': '/api/auth/',
            'inventory': '/api/inventory/',
            'forecasting': '/api/forecasting/',
            'risk_management': '/api/risk/',
            'copilot': '/api/copilot/',
            'shared': '/api/shared/'
        }
    })

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
    # API root
    path('api/', api_root, name='api_root'),
    
    # Authentication endpoints
    path('api/auth/', include([
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    ])),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Microservice endpoints
    path('api/inventory/', include('inventory.urls')),
    path('api/forecasting/', include('forecasting.urls')),
    path('api/risk/', include('risk_management.urls')),
    path('api/copilot/', include('copilot.urls')),
    path('api/shared/', include('shared.urls')),
    
    # Monitoring endpoints
    path('metrics/', include('django_prometheus.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Add development-only endpoints
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# Custom error handlers
handler404 = 'shared.views.custom_404'
handler500 = 'shared.views.custom_500'
