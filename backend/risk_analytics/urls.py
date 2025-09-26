from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'risk-events', views.RiskEventViewSet, basename='riskevent')
router.register(r'risk-scores', views.RiskScoreViewSet, basename='riskscore')
router.register(r'anomalies', views.AnomalyViewSet, basename='anomaly')
router.register(r'supplier-kpis', views.SupplierKPIViewSet, basename='supplierkpi')

# The API URLs are now determined automatically by the router
urlpatterns = [
    # API root
    path('api/v1/', include(router.urls)),
    
    # Custom endpoints for risk analytics
    path('api/v1/risk-events/<int:pk>/score/', views.RiskEventViewSet.as_view({'post': 'calculate_score'}), name='riskevent-calculate-score'),
    path('api/v1/suppliers/<int:supplier_id>/risk-summary/', views.SupplierRiskSummaryView.as_view(), name='supplier-risk-summary'),
    path('api/v1/analytics/risk-trends/', views.RiskTrendsAnalyticsView.as_view(), name='risk-trends'),
    path('api/v1/analytics/anomaly-trends/', views.AnomalyTrendsAnalyticsView.as_view(), name='anomaly-trends'),
    path('api/v1/analytics/kpi-trends/', views.KPITrendsAnalyticsView.as_view(), name='kpi-trends'),
    path('api/v1/analytics/dashboard/', views.DashboardAnalyticsView.as_view(), name='dashboard-analytics'),
    
    # Bulk operations
    path('api/v1/risk-events/bulk-create/', views.BulkRiskEventCreateView.as_view(), name='bulk-risk-events'),
    path('api/v1/risk-scores/bulk-update/', views.BulkRiskScoreUpdateView.as_view(), name='bulk-risk-scores'),
    
    # Anomaly detection endpoints
    path('api/v1/anomalies/detect/', views.AnomalyDetectionView.as_view(), name='detect-anomalies'),
    path('api/v1/anomalies/by-supplier/<int:supplier_id>/', views.SupplierAnomalyView.as_view(), name='supplier-anomalies'),
]
