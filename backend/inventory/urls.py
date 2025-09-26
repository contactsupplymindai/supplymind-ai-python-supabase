from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse

from .views import (
    ProductViewSet, ProductCategoryViewSet, SupplierViewSet,
    InventoryItemViewSet, WarehouseViewSet, StockMovementViewSet,
    ProductVariantViewSet, StockAlertViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', ProductCategoryViewSet, basename='productcategory')
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'inventory', InventoryItemViewSet, basename='inventoryitem')
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'movements', StockMovementViewSet, basename='stockmovement')
router.register(r'variants', ProductVariantViewSet, basename='productvariant')
router.register(r'alerts', StockAlertViewSet, basename='stockalert')


@api_view(['GET'])
def inventory_api_root(request):
    """
    Inventory Management API Root Endpoint
    
    This API provides comprehensive inventory management functionality
    including products, suppliers, warehouses, stock tracking, and more.
    """
    api_endpoints = {
        'products': request.build_absolute_uri('products/'),
        'categories': request.build_absolute_uri('categories/'),
        'suppliers': request.build_absolute_uri('suppliers/'),
        'inventory': request.build_absolute_uri('inventory/'),
        'warehouses': request.build_absolute_uri('warehouses/'),
        'movements': request.build_absolute_uri('movements/'),
        'variants': request.build_absolute_uri('variants/'),
        'alerts': request.build_absolute_uri('alerts/'),
    }
    
    return Response({
        'message': 'Inventory Management REST API',
        'version': '1.0.0',
        'description': 'CRUD operations for inventory management using shared models and Supabase DB',
        'endpoints': api_endpoints,
        'features': [
            'Product management with categories and variants',
            'Supplier management',
            'Multi-warehouse inventory tracking',
            'Stock movement history',
            'Automated stock alerts',
            'Advanced filtering and search',
            'Stock adjustment operations'
        ]
    })


@api_view(['GET'])
def api_health(request):
    """
    API Health Check Endpoint
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'inventory-api',
        'database': 'supabase',
        'version': '1.0.0'
    })


# The API URLs
urlpatterns = [
    # API root endpoint
    path('', inventory_api_root, name='inventory-api-root'),
    
    # Health check
    path('health/', api_health, name='inventory-api-health'),
    
    # Include all the router URLs
    path('', include(router.urls)),
]

"""
API Endpoint Structure:

Base URL: /api/inventory/

- GET  /api/inventory/ - API root with documentation
- GET  /api/inventory/health/ - Health check

Products:
- GET    /api/inventory/products/ - List products
- POST   /api/inventory/products/ - Create product
- GET    /api/inventory/products/{id}/ - Retrieve product
- PUT    /api/inventory/products/{id}/ - Update product
- DELETE /api/inventory/products/{id}/ - Delete product
- POST   /api/inventory/products/{id}/activate/ - Activate product
- POST   /api/inventory/products/{id}/deactivate/ - Deactivate product

Categories:
- GET    /api/inventory/categories/ - List categories
- POST   /api/inventory/categories/ - Create category
- GET    /api/inventory/categories/{id}/ - Retrieve category
- PUT    /api/inventory/categories/{id}/ - Update category
- DELETE /api/inventory/categories/{id}/ - Delete category

Suppliers:
- GET    /api/inventory/suppliers/ - List suppliers
- POST   /api/inventory/suppliers/ - Create supplier
- GET    /api/inventory/suppliers/{id}/ - Retrieve supplier
- PUT    /api/inventory/suppliers/{id}/ - Update supplier
- DELETE /api/inventory/suppliers/{id}/ - Delete supplier
- GET    /api/inventory/suppliers/{id}/products/ - Get supplier products

Inventory Items:
- GET    /api/inventory/inventory/ - List inventory items
- POST   /api/inventory/inventory/ - Create inventory item
- GET    /api/inventory/inventory/{id}/ - Retrieve inventory item
- PUT    /api/inventory/inventory/{id}/ - Update inventory item
- DELETE /api/inventory/inventory/{id}/ - Delete inventory item
- POST   /api/inventory/inventory/{id}/adjust_stock/ - Adjust stock
- GET    /api/inventory/inventory/low_stock/ - Get low stock items

Warehouses:
- GET    /api/inventory/warehouses/ - List warehouses
- POST   /api/inventory/warehouses/ - Create warehouse
- GET    /api/inventory/warehouses/{id}/ - Retrieve warehouse
- PUT    /api/inventory/warehouses/{id}/ - Update warehouse
- DELETE /api/inventory/warehouses/{id}/ - Delete warehouse
- GET    /api/inventory/warehouses/{id}/inventory/ - Get warehouse inventory
- GET    /api/inventory/warehouses/{id}/stock_summary/ - Get stock summary

Stock Movements (Read-only):
- GET    /api/inventory/movements/ - List stock movements
- GET    /api/inventory/movements/{id}/ - Retrieve stock movement
- GET    /api/inventory/movements/recent/ - Get recent movements

Product Variants:
- GET    /api/inventory/variants/ - List product variants
- POST   /api/inventory/variants/ - Create variant
- GET    /api/inventory/variants/{id}/ - Retrieve variant
- PUT    /api/inventory/variants/{id}/ - Update variant
- DELETE /api/inventory/variants/{id}/ - Delete variant

Stock Alerts:
- GET    /api/inventory/alerts/ - List stock alerts
- POST   /api/inventory/alerts/ - Create alert
- GET    /api/inventory/alerts/{id}/ - Retrieve alert
- PUT    /api/inventory/alerts/{id}/ - Update alert
- DELETE /api/inventory/alerts/{id}/ - Delete alert
- POST   /api/inventory/alerts/{id}/resolve/ - Resolve alert
- GET    /api/inventory/alerts/unresolved/ - Get unresolved alerts
"""
