import django_filters
from django_filters import rest_framework as filters
from shared.models import PurchaseOrder, SalesOrder
from django.db import models


class PurchaseOrderFilter(filters.FilterSet):
    """Filter set for Purchase Orders with advanced filtering options."""
    
    # Date range filters
    order_date_from = filters.DateFilter(field_name='order_date', lookup_expr='gte')
    order_date_to = filters.DateFilter(field_name='order_date', lookup_expr='lte')
    delivery_date_from = filters.DateFilter(field_name='delivery_date', lookup_expr='gte')
    delivery_date_to = filters.DateFilter(field_name='delivery_date', lookup_expr='lte')
    created_from = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_to = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Amount range filters
    min_amount = filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    
    # Status filters
    status = filters.ChoiceFilter(
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ]
    )
    
    # Multi-status filter
    status_in = filters.BaseInFilter(
        field_name='status',
        help_text='Filter by multiple statuses (comma-separated)'
    )
    
    # Supplier filters
    supplier = filters.NumberFilter(field_name='supplier_id')
    supplier_name = filters.CharFilter(
        field_name='supplier__name', 
        lookup_expr='icontains'
    )
    
    # Text search filters
    search = filters.CharFilter(method='filter_search')
    order_number = filters.CharFilter(
        field_name='order_number', 
        lookup_expr='icontains'
    )
    description = filters.CharFilter(
        field_name='description', 
        lookup_expr='icontains'
    )
    
    # User filters
    created_by = filters.NumberFilter(field_name='created_by_id')
    approved_by = filters.NumberFilter(field_name='approved_by_id')
    
    # Boolean filters
    is_approved = filters.BooleanFilter(method='filter_is_approved')
    is_overdue = filters.BooleanFilter(method='filter_is_overdue')
    has_items = filters.BooleanFilter(method='filter_has_items')
    
    class Meta:
        model = PurchaseOrder
        fields = {
            'total_amount': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'order_date': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'delivery_date': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'status': ['exact'],
            'supplier': ['exact'],
        }
    
    def filter_search(self, queryset, name, value):
        """Global search across multiple fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            models.Q(order_number__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(notes__icontains=value) |
            models.Q(supplier__name__icontains=value)
        )
    
    def filter_is_approved(self, queryset, name, value):
        """Filter by approval status."""
        if value is True:
            return queryset.filter(approved_by__isnull=False)
        elif value is False:
            return queryset.filter(approved_by__isnull=True)
        return queryset
    
    def filter_is_overdue(self, queryset, name, value):
        """Filter orders that are overdue for delivery."""
        from django.utils import timezone
        today = timezone.now().date()
        
        if value is True:
            return queryset.filter(
                delivery_date__lt=today,
                status__in=['pending', 'approved']
            )
        elif value is False:
            return queryset.exclude(
                delivery_date__lt=today,
                status__in=['pending', 'approved']
            )
        return queryset
    
    def filter_has_items(self, queryset, name, value):
        """Filter orders that have or don't have items."""
        if value is True:
            return queryset.filter(items__isnull=False).distinct()
        elif value is False:
            return queryset.filter(items__isnull=True)
        return queryset


class SalesOrderFilter(filters.FilterSet):
    """Filter set for Sales Orders with advanced filtering options."""
    
    # Date range filters
    order_date_from = filters.DateFilter(field_name='order_date', lookup_expr='gte')
    order_date_to = filters.DateFilter(field_name='order_date', lookup_expr='lte')
    delivery_date_from = filters.DateFilter(field_name='delivery_date', lookup_expr='gte')
    delivery_date_to = filters.DateFilter(field_name='delivery_date', lookup_expr='lte')
    created_from = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_to = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Amount range filters
    min_amount = filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    
    # Status filters
    status = filters.ChoiceFilter(
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('shipped', 'Shipped'),
            ('delivered', 'Delivered'),
            ('cancelled', 'Cancelled'),
        ]
    )
    
    # Multi-status filter
    status_in = filters.BaseInFilter(
        field_name='status',
        help_text='Filter by multiple statuses (comma-separated)'
    )
    
    # Customer filters
    customer = filters.NumberFilter(field_name='customer_id')
    customer_name = filters.CharFilter(
        field_name='customer__name', 
        lookup_expr='icontains'
    )
    
    # Text search filters
    search = filters.CharFilter(method='filter_search')
    order_number = filters.CharFilter(
        field_name='order_number', 
        lookup_expr='icontains'
    )
    description = filters.CharFilter(
        field_name='description', 
        lookup_expr='icontains'
    )
    
    # User filters
    created_by = filters.NumberFilter(field_name='created_by_id')
    confirmed_by = filters.NumberFilter(field_name='confirmed_by_id')
    
    # Boolean filters
    is_confirmed = filters.BooleanFilter(method='filter_is_confirmed')
    is_shipped = filters.BooleanFilter(method='filter_is_shipped')
    is_overdue = filters.BooleanFilter(method='filter_is_overdue')
    has_items = filters.BooleanFilter(method='filter_has_items')
    
    class Meta:
        model = SalesOrder
        fields = {
            'total_amount': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'order_date': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'delivery_date': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'status': ['exact'],
            'customer': ['exact'],
        }
    
    def filter_search(self, queryset, name, value):
        """Global search across multiple fields."""
        if not value:
            return queryset
        
        return queryset.filter(
            models.Q(order_number__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(notes__icontains=value) |
            models.Q(customer__name__icontains=value)
        )
    
    def filter_is_confirmed(self, queryset, name, value):
        """Filter by confirmation status."""
        if value is True:
            return queryset.filter(confirmed_by__isnull=False)
        elif value is False:
            return queryset.filter(confirmed_by__isnull=True)
        return queryset
    
    def filter_is_shipped(self, queryset, name, value):
        """Filter by shipping status."""
        if value is True:
            return queryset.filter(shipped_at__isnull=False)
        elif value is False:
            return queryset.filter(shipped_at__isnull=True)
        return queryset
    
    def filter_is_overdue(self, queryset, name, value):
        """Filter orders that are overdue for delivery."""
        from django.utils import timezone
        today = timezone.now().date()
        
        if value is True:
            return queryset.filter(
                delivery_date__lt=today,
                status__in=['pending', 'confirmed', 'shipped']
            )
        elif value is False:
            return queryset.exclude(
                delivery_date__lt=today,
                status__in=['pending', 'confirmed', 'shipped']
            )
        return queryset
    
    def filter_has_items(self, queryset, name, value):
        """Filter orders that have or don't have items."""
        if value is True:
            return queryset.filter(items__isnull=False).distinct()
        elif value is False:
            return queryset.filter(items__isnull=True)
        return queryset
