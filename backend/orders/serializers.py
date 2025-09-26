from rest_framework import serializers
from shared.models import PurchaseOrder, SalesOrder, PurchaseOrderItem, SalesOrderItem
from django.contrib.auth import get_user_model

User = get_user_model()


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for Purchase Order Items."""
    
    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id', 'product_id', 'product_name', 'quantity', 
            'unit_price', 'total_price', 'description'
        ]
        read_only_fields = ['id', 'total_price']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for reading Purchase Orders."""
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.username', read_only=True)
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'id', 'order_number', 'supplier', 'supplier_name',
            'order_date', 'delivery_date', 'status', 'total_amount',
            'description', 'notes', 'created_by', 'created_by_name',
            'approved_by', 'approved_by_name', 'approved_at',
            'cancelled_at', 'delivered_at', 'created_at', 'updated_at',
            'items'
        ]
        read_only_fields = [
            'id', 'order_number', 'created_by', 'approved_by',
            'approved_at', 'cancelled_at', 'delivered_at',
            'created_at', 'updated_at'
        ]


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Purchase Orders."""
    items = PurchaseOrderItemSerializer(many=True, required=False)
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'supplier', 'order_date', 'delivery_date', 'total_amount',
            'description', 'notes', 'items'
        ]
    
    def create(self, validated_data):
        """Create a new purchase order with items."""
        items_data = validated_data.pop('items', [])
        validated_data['created_by'] = self.context['request'].user
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        
        # Create order items
        for item_data in items_data:
            PurchaseOrderItem.objects.create(
                purchase_order=purchase_order,
                **item_data
            )
        
        return purchase_order
    
    def update(self, instance, validated_data):
        """Update a purchase order and its items."""
        items_data = validated_data.pop('items', [])
        
        # Update the main order
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle items update (replace all items)
        if items_data:
            instance.items.all().delete()
            for item_data in items_data:
                PurchaseOrderItem.objects.create(
                    purchase_order=instance,
                    **item_data
                )
        
        return instance
    
    def validate(self, data):
        """Validate purchase order data."""
        # Ensure delivery date is after order date
        if data.get('delivery_date') and data.get('order_date'):
            if data['delivery_date'] < data['order_date']:
                raise serializers.ValidationError(
                    "Delivery date cannot be before order date."
                )
        
        # Validate total amount is positive
        if data.get('total_amount') and data['total_amount'] <= 0:
            raise serializers.ValidationError(
                "Total amount must be greater than zero."
            )
        
        return data


class SalesOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for Sales Order Items."""
    
    class Meta:
        model = SalesOrderItem
        fields = [
            'id', 'product_id', 'product_name', 'quantity', 
            'unit_price', 'total_price', 'description'
        ]
        read_only_fields = ['id', 'total_price']


class SalesOrderSerializer(serializers.ModelSerializer):
    """Serializer for reading Sales Orders."""
    items = SalesOrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    confirmed_by_name = serializers.CharField(source='confirmed_by.username', read_only=True)
    
    class Meta:
        model = SalesOrder
        fields = [
            'id', 'order_number', 'customer', 'customer_name',
            'order_date', 'delivery_date', 'status', 'total_amount',
            'description', 'notes', 'created_by', 'created_by_name',
            'confirmed_by', 'confirmed_by_name', 'confirmed_at',
            'shipped_at', 'delivered_at', 'cancelled_at',
            'created_at', 'updated_at', 'items'
        ]
        read_only_fields = [
            'id', 'order_number', 'created_by', 'confirmed_by',
            'confirmed_at', 'shipped_at', 'delivered_at', 'cancelled_at',
            'created_at', 'updated_at'
        ]


class SalesOrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating Sales Orders."""
    items = SalesOrderItemSerializer(many=True, required=False)
    
    class Meta:
        model = SalesOrder
        fields = [
            'customer', 'order_date', 'delivery_date', 'total_amount',
            'description', 'notes', 'items'
        ]
    
    def create(self, validated_data):
        """Create a new sales order with items."""
        items_data = validated_data.pop('items', [])
        validated_data['created_by'] = self.context['request'].user
        sales_order = SalesOrder.objects.create(**validated_data)
        
        # Create order items
        for item_data in items_data:
            SalesOrderItem.objects.create(
                sales_order=sales_order,
                **item_data
            )
        
        return sales_order
    
    def update(self, instance, validated_data):
        """Update a sales order and its items."""
        items_data = validated_data.pop('items', [])
        
        # Update the main order
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Handle items update (replace all items)
        if items_data:
            instance.items.all().delete()
            for item_data in items_data:
                SalesOrderItem.objects.create(
                    sales_order=instance,
                    **item_data
                )
        
        return instance
    
    def validate(self, data):
        """Validate sales order data."""
        # Ensure delivery date is after order date
        if data.get('delivery_date') and data.get('order_date'):
            if data['delivery_date'] < data['order_date']:
                raise serializers.ValidationError(
                    "Delivery date cannot be before order date."
                )
        
        # Validate total amount is positive
        if data.get('total_amount') and data['total_amount'] <= 0:
            raise serializers.ValidationError(
                "Total amount must be greater than zero."
            )
        
        return data


class OrderAnalyticsSerializer(serializers.Serializer):
    """Serializer for order analytics data."""
    total_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    confirmed_orders = serializers.IntegerField(required=False)
    approved_orders = serializers.IntegerField(required=False)
    shipped_orders = serializers.IntegerField(required=False)
    delivered_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    average_order_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    monthly_value = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    monthly_revenue = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    monthly_orders = serializers.IntegerField()


class OrderStatusUpdateSerializer(serializers.Serializer):
    """Serializer for order status updates."""
    status = serializers.ChoiceField(
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('confirmed', 'Confirmed'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ]
    )
    notes = serializers.CharField(max_length=500, required=False)


class RevenueDataSerializer(serializers.Serializer):
    """Serializer for revenue trend data."""
    date = serializers.DateField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    orders = serializers.IntegerField()


class RevenueTrendsSerializer(serializers.Serializer):
    """Serializer for revenue trends response."""
    period_days = serializers.IntegerField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    daily_data = RevenueDataSerializer(many=True)
