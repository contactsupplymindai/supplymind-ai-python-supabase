from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from shared.models import (
    Product, ProductCategory, Supplier, InventoryItem,
    Warehouse, StockMovement, ProductVariant, StockAlert
)
from .serializers import (
    ProductSerializer, ProductCategorySerializer, SupplierSerializer,
    InventoryItemSerializer, WarehouseSerializer, StockMovementSerializer,
    ProductVariantSerializer, StockAlertSerializer
)


class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Product model.
    Provides list, create, retrieve, update, delete functionality.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'supplier', 'is_active']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at', 'price']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a product"""
        product = self.get_object()
        product.is_active = True
        product.save()
        return Response({'status': 'product activated'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a product"""
        product = self.get_object()
        product.is_active = False
        product.save()
        return Response({'status': 'product deactivated'})


class ProductCategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for ProductCategory model.
    """
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class SupplierViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Supplier model.
    """
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'contact_person', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get all products from this supplier"""
        supplier = self.get_object()
        products = Product.objects.filter(supplier=supplier)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class InventoryItemViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for InventoryItem model.
    """
    queryset = InventoryItem.objects.select_related('product', 'warehouse').all()
    serializer_class = InventoryItemSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product', 'warehouse', 'is_tracked']
    search_fields = ['product__name', 'product__sku', 'warehouse__name']
    ordering_fields = ['quantity', 'minimum_stock_level', 'updated_at']
    ordering = ['-updated_at']

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """Adjust stock quantity for an inventory item"""
        inventory_item = self.get_object()
        adjustment = request.data.get('adjustment', 0)
        reason = request.data.get('reason', 'Manual adjustment')
        
        with transaction.atomic():
            old_quantity = inventory_item.quantity
            inventory_item.quantity += adjustment
            inventory_item.save()
            
            # Create stock movement record
            StockMovement.objects.create(
                inventory_item=inventory_item,
                movement_type='adjustment',
                quantity=adjustment,
                reason=reason,
                previous_quantity=old_quantity,
                new_quantity=inventory_item.quantity
            )
        
        return Response({
            'status': 'stock adjusted',
            'old_quantity': old_quantity,
            'new_quantity': inventory_item.quantity,
            'adjustment': adjustment
        })

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get items with low stock (quantity <= minimum_stock_level)"""
        low_stock_items = self.queryset.filter(
            quantity__lte=models.F('minimum_stock_level')
        )
        serializer = self.get_serializer(low_stock_items, many=True)
        return Response(serializer.data)


class WarehouseViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Warehouse model.
    """
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'location', 'manager_name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        """Get all inventory items in this warehouse"""
        warehouse = self.get_object()
        inventory_items = InventoryItem.objects.filter(warehouse=warehouse)
        serializer = InventoryItemSerializer(inventory_items, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stock_summary(self, request, pk=None):
        """Get stock summary for this warehouse"""
        warehouse = self.get_object()
        inventory_items = InventoryItem.objects.filter(warehouse=warehouse)
        
        total_items = inventory_items.count()
        total_quantity = sum(item.quantity for item in inventory_items)
        low_stock_count = inventory_items.filter(
            quantity__lte=models.F('minimum_stock_level')
        ).count()
        
        return Response({
            'warehouse': warehouse.name,
            'total_items': total_items,
            'total_quantity': total_quantity,
            'low_stock_count': low_stock_count
        })


class StockMovementViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for StockMovement model.
    Read-only by default as movements are typically created by system actions.
    """
    queryset = StockMovement.objects.select_related(
        'inventory_item__product', 'inventory_item__warehouse'
    ).all()
    serializer_class = StockMovementSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['movement_type', 'inventory_item', 'created_at']
    search_fields = ['reason', 'inventory_item__product__name']
    ordering_fields = ['created_at', 'quantity']
    ordering = ['-created_at']
    
    # Override to make it read-only by default
    http_method_names = ['get', 'head', 'options']

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent stock movements (last 100)"""
        recent_movements = self.queryset[:100]
        serializer = self.get_serializer(recent_movements, many=True)
        return Response(serializer.data)


class ProductVariantViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for ProductVariant model.
    """
    queryset = ProductVariant.objects.select_related('product').all()
    serializer_class = ProductVariantSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product', 'is_active']
    search_fields = ['variant_name', 'sku', 'product__name']
    ordering_fields = ['variant_name', 'price', 'created_at']
    ordering = ['variant_name']


class StockAlertViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for StockAlert model.
    """
    queryset = StockAlert.objects.select_related(
        'inventory_item__product', 'inventory_item__warehouse'
    ).all()
    serializer_class = StockAlertSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['alert_type', 'is_resolved', 'inventory_item']
    search_fields = ['message', 'inventory_item__product__name']
    ordering_fields = ['created_at', 'alert_type']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark alert as resolved"""
        alert = self.get_object()
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save()
        return Response({'status': 'alert resolved'})

    @action(detail=False, methods=['get'])
    def unresolved(self, request):
        """Get all unresolved alerts"""
        unresolved_alerts = self.queryset.filter(is_resolved=False)
        serializer = self.get_serializer(unresolved_alerts, many=True)
        return Response(serializer.data)
