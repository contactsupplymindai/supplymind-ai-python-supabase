from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for automatic URL routing
router = DefaultRouter()
router.register(r'purchase-orders', views.PurchaseOrderViewSet, basename='purchaseorder')
router.register(r'sales-orders', views.SalesOrderViewSet, basename='salesorder')

app_name = 'orders'

urlpatterns = [
    # Include router URLs for viewsets
    path('api/', include(router.urls)),
    
    # Additional custom endpoints if needed
    path('api/purchase-orders/<int:pk>/approve/', 
         views.PurchaseOrderViewSet.as_view({'post': 'approve'}), 
         name='purchase-order-approve'),
    
    path('api/purchase-orders/<int:pk>/cancel/', 
         views.PurchaseOrderViewSet.as_view({'post': 'cancel'}), 
         name='purchase-order-cancel'),
    
    path('api/purchase-orders/<int:pk>/mark-delivered/', 
         views.PurchaseOrderViewSet.as_view({'post': 'mark_delivered'}), 
         name='purchase-order-mark-delivered'),
    
    path('api/purchase-orders/analytics/', 
         views.PurchaseOrderViewSet.as_view({'get': 'analytics'}), 
         name='purchase-order-analytics'),
    
    path('api/sales-orders/<int:pk>/confirm/', 
         views.SalesOrderViewSet.as_view({'post': 'confirm'}), 
         name='sales-order-confirm'),
    
    path('api/sales-orders/<int:pk>/ship/', 
         views.SalesOrderViewSet.as_view({'post': 'ship'}), 
         name='sales-order-ship'),
    
    path('api/sales-orders/<int:pk>/deliver/', 
         views.SalesOrderViewSet.as_view({'post': 'deliver'}), 
         name='sales-order-deliver'),
    
    path('api/sales-orders/<int:pk>/cancel/', 
         views.SalesOrderViewSet.as_view({'post': 'cancel'}), 
         name='sales-order-cancel'),
    
    path('api/sales-orders/analytics/', 
         views.SalesOrderViewSet.as_view({'get': 'analytics'}), 
         name='sales-order-analytics'),
    
    path('api/sales-orders/revenue-trends/', 
         views.SalesOrderViewSet.as_view({'get': 'revenue_trends'}), 
         name='sales-order-revenue-trends'),
]

# Available endpoints:
# 
# Purchase Orders:
# GET    /api/purchase-orders/                    - List all purchase orders
# POST   /api/purchase-orders/                    - Create new purchase order  
# GET    /api/purchase-orders/{id}/               - Get specific purchase order
# PUT    /api/purchase-orders/{id}/               - Update purchase order
# PATCH  /api/purchase-orders/{id}/               - Partial update purchase order
# DELETE /api/purchase-orders/{id}/               - Delete purchase order
# POST   /api/purchase-orders/{id}/approve/       - Approve purchase order
# POST   /api/purchase-orders/{id}/cancel/        - Cancel purchase order
# POST   /api/purchase-orders/{id}/mark-delivered/ - Mark as delivered
# GET    /api/purchase-orders/analytics/          - Get purchase order analytics
#
# Sales Orders:
# GET    /api/sales-orders/                       - List all sales orders
# POST   /api/sales-orders/                       - Create new sales order
# GET    /api/sales-orders/{id}/                  - Get specific sales order
# PUT    /api/sales-orders/{id}/                  - Update sales order
# PATCH  /api/sales-orders/{id}/                  - Partial update sales order
# DELETE /api/sales-orders/{id}/                  - Delete sales order
# POST   /api/sales-orders/{id}/confirm/          - Confirm sales order
# POST   /api/sales-orders/{id}/ship/             - Mark as shipped
# POST   /api/sales-orders/{id}/deliver/          - Mark as delivered
# POST   /api/sales-orders/{id}/cancel/           - Cancel sales order
# GET    /api/sales-orders/analytics/             - Get sales order analytics
# GET    /api/sales-orders/revenue-trends/        - Get revenue trends
#
# Query Parameters (for both endpoints):
# - status: Filter by status
# - start_date, end_date: Date range filtering
# - supplier_id / customer_id: Filter by supplier/customer
# - search: Global text search
# - min_amount, max_amount: Amount range filtering
# - ordering: Sort results (e.g., -created_at, total_amount)
# - page, page_size: Pagination
