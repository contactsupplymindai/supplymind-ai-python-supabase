from rest_framework import serializers
from django.utils import timezone

from shared.models import (
    Product, ProductCategory, Supplier, InventoryItem,
    Warehouse, StockMovement, ProductVariant, StockAlert
)


class ProductCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for ProductCategory model.
    """
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'description', 'parent_category', 
                 'created_at', 'updated_at', 'product_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 'product_count']
    
    def get_product_count(self, obj):
        """Return the number of products in this category"""
        return obj.products.count() if hasattr(obj, 'products') else 0


class SupplierSerializer(serializers.ModelSerializer):
    """
    Serializer for Supplier model.
    """
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_person', 'email', 'phone',
                 'address', 'website', 'is_active', 'created_at', 
                 'updated_at', 'product_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 'product_count']
    
    def get_product_count(self, obj):
        """Return the number of products from this supplier"""
        return obj.products.count() if hasattr(obj, 'products') else 0


class ProductVariantSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductVariant model.
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = ['id', 'product', 'product_name', 'variant_name', 
                 'sku', 'price', 'cost', 'weight', 'dimensions',
                 'attributes', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'product_name']


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model with nested relationships.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    total_inventory = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'sku', 'category', 
                 'category_name', 'supplier', 'supplier_name', 'price', 
                 'cost', 'weight', 'dimensions', 'attributes', 'is_active',
                 'created_at', 'updated_at', 'variants', 'total_inventory']
        read_only_fields = ['id', 'created_at', 'updated_at', 'category_name', 
                           'supplier_name', 'variants', 'total_inventory']
    
    def get_total_inventory(self, obj):
        """Return total inventory quantity across all warehouses"""
        inventory_items = obj.inventory_items.all()
        return sum(item.quantity for item in inventory_items)


class WarehouseSerializer(serializers.ModelSerializer):
    """
    Serializer for Warehouse model.
    """
    inventory_count = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'location', 'manager_name', 'manager_email',
                 'phone', 'is_active', 'created_at', 'updated_at',
                 'inventory_count', 'total_stock']
        read_only_fields = ['id', 'created_at', 'updated_at', 
                           'inventory_count', 'total_stock']
    
    def get_inventory_count(self, obj):
        """Return the number of inventory items in this warehouse"""
        return obj.inventory_items.count()
    
    def get_total_stock(self, obj):
        """Return total stock quantity in this warehouse"""
        inventory_items = obj.inventory_items.all()
        return sum(item.quantity for item in inventory_items)


class InventoryItemSerializer(serializers.ModelSerializer):
    """
    Serializer for InventoryItem model with detailed product and warehouse info.
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    stock_status = serializers.SerializerMethodField()
    days_since_last_movement = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryItem
        fields = ['id', 'product', 'product_name', 'product_sku', 
                 'warehouse', 'warehouse_name', 'quantity', 
                 'minimum_stock_level', 'maximum_stock_level',
                 'reorder_point', 'location_in_warehouse', 'is_tracked',
                 'created_at', 'updated_at', 'stock_status', 
                 'days_since_last_movement']
        read_only_fields = ['id', 'created_at', 'updated_at', 'product_name',
                           'product_sku', 'warehouse_name', 'stock_status',
                           'days_since_last_movement']
    
    def get_stock_status(self, obj):
        """Return stock status based on quantity levels"""
        if obj.quantity <= 0:
            return 'out_of_stock'
        elif obj.minimum_stock_level and obj.quantity <= obj.minimum_stock_level:
            return 'low_stock'
        elif obj.maximum_stock_level and obj.quantity >= obj.maximum_stock_level:
            return 'overstock'
        else:
            return 'normal'
    
    def get_days_since_last_movement(self, obj):
        """Return days since last stock movement"""
        last_movement = obj.stock_movements.order_by('-created_at').first()
        if last_movement:
            delta = timezone.now() - last_movement.created_at
            return delta.days
        return None


class StockMovementSerializer(serializers.ModelSerializer):
    """
    Serializer for StockMovement model with detailed context.
    """
    product_name = serializers.CharField(
        source='inventory_item.product.name', read_only=True
    )
    product_sku = serializers.CharField(
        source='inventory_item.product.sku', read_only=True
    )
    warehouse_name = serializers.CharField(
        source='inventory_item.warehouse.name', read_only=True
    )
    
    class Meta:
        model = StockMovement
        fields = ['id', 'inventory_item', 'product_name', 'product_sku',
                 'warehouse_name', 'movement_type', 'quantity', 'reason',
                 'reference_number', 'previous_quantity', 'new_quantity',
                 'created_at', 'created_by']
        read_only_fields = ['id', 'created_at', 'product_name', 
                           'product_sku', 'warehouse_name']


class StockAlertSerializer(serializers.ModelSerializer):
    """
    Serializer for StockAlert model with inventory context.
    """
    product_name = serializers.CharField(
        source='inventory_item.product.name', read_only=True
    )
    product_sku = serializers.CharField(
        source='inventory_item.product.sku', read_only=True
    )
    warehouse_name = serializers.CharField(
        source='inventory_item.warehouse.name', read_only=True
    )
    current_quantity = serializers.IntegerField(
        source='inventory_item.quantity', read_only=True
    )
    
    class Meta:
        model = StockAlert
        fields = ['id', 'inventory_item', 'product_name', 'product_sku',
                 'warehouse_name', 'current_quantity', 'alert_type', 
                 'message', 'threshold_value', 'is_resolved', 
                 'resolved_at', 'created_at']
        read_only_fields = ['id', 'created_at', 'product_name', 'product_sku',
                           'warehouse_name', 'current_quantity']


# Lightweight serializers for dropdowns and selections
class ProductSimpleSerializer(serializers.ModelSerializer):
    """Simplified Product serializer for dropdowns"""
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku']


class WarehouseSimpleSerializer(serializers.ModelSerializer):
    """Simplified Warehouse serializer for dropdowns"""
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'location']


class SupplierSimpleSerializer(serializers.ModelSerializer):
    """Simplified Supplier serializer for dropdowns"""
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_person']
