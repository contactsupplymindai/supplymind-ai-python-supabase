from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from shared.models import PurchaseOrder, SalesOrder
from .serializers import (
    PurchaseOrderSerializer,
    SalesOrderSerializer,
    PurchaseOrderCreateSerializer,
    SalesOrderCreateSerializer,
    OrderAnalyticsSerializer
)
from .filters import PurchaseOrderFilter, SalesOrderFilter


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Purchase Orders with full CRUD operations."""
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PurchaseOrderFilter
    search_fields = ['order_number', 'supplier__name', 'description']
    ordering_fields = ['created_at', 'order_date', 'delivery_date', 'total_amount']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Use different serializers for create/update vs. read operations."""
        if self.action in ['create', 'update', 'partial_update']:
            return PurchaseOrderCreateSerializer
        return PurchaseOrderSerializer

    def get_queryset(self):
        """Filter queryset based on user permissions and query parameters."""
        queryset = super().get_queryset()
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(order_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(order_date__lte=end_date)
        
        # Filter by supplier
        supplier_id = self.request.query_params.get('supplier_id')
        if supplier_id:
            queryset = queryset.filter(supplier_id=supplier_id)
            
        return queryset.select_related('supplier').prefetch_related('items')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a purchase order."""
        order = self.get_object()
        if order.status != 'pending':
            return Response(
                {'error': 'Only pending orders can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'approved'
        order.approved_by = request.user
        order.approved_at = timezone.now()
        order.save()
        
        return Response(
            {'message': 'Purchase order approved successfully'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a purchase order."""
        order = self.get_object()
        if order.status in ['delivered', 'cancelled']:
            return Response(
                {'error': 'Cannot cancel delivered or already cancelled orders'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.cancelled_at = timezone.now()
        order.save()
        
        return Response(
            {'message': 'Purchase order cancelled successfully'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        """Mark a purchase order as delivered."""
        order = self.get_object()
        if order.status != 'approved':
            return Response(
                {'error': 'Only approved orders can be marked as delivered'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'delivered'
        order.delivered_at = timezone.now()
        order.save()
        
        return Response(
            {'message': 'Purchase order marked as delivered'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get purchase order analytics."""
        queryset = self.get_queryset()
        
        # Basic counts
        total_orders = queryset.count()
        pending_orders = queryset.filter(status='pending').count()
        approved_orders = queryset.filter(status='approved').count()
        delivered_orders = queryset.filter(status='delivered').count()
        cancelled_orders = queryset.filter(status='cancelled').count()
        
        # Financial analytics
        total_value = queryset.aggregate(total=Sum('total_amount'))['total'] or 0
        avg_order_value = queryset.aggregate(avg=Avg('total_amount'))['avg'] or 0
        
        # Time-based analytics
        today = timezone.now().date()
        this_month = queryset.filter(order_date__month=today.month, order_date__year=today.year)
        monthly_value = this_month.aggregate(total=Sum('total_amount'))['total'] or 0
        
        analytics_data = {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'approved_orders': approved_orders,
            'delivered_orders': delivered_orders,
            'cancelled_orders': cancelled_orders,
            'total_value': total_value,
            'average_order_value': avg_order_value,
            'monthly_value': monthly_value,
            'monthly_orders': this_month.count()
        }
        
        return Response(analytics_data, status=status.HTTP_200_OK)


class SalesOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Sales Orders with full CRUD operations."""
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SalesOrderFilter
    search_fields = ['order_number', 'customer__name', 'description']
    ordering_fields = ['created_at', 'order_date', 'delivery_date', 'total_amount']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Use different serializers for create/update vs. read operations."""
        if self.action in ['create', 'update', 'partial_update']:
            return SalesOrderCreateSerializer
        return SalesOrderSerializer

    def get_queryset(self):
        """Filter queryset based on user permissions and query parameters."""
        queryset = super().get_queryset()
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(order_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(order_date__lte=end_date)
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
            
        return queryset.select_related('customer').prefetch_related('items')

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm a sales order."""
        order = self.get_object()
        if order.status != 'pending':
            return Response(
                {'error': 'Only pending orders can be confirmed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'confirmed'
        order.confirmed_by = request.user
        order.confirmed_at = timezone.now()
        order.save()
        
        return Response(
            {'message': 'Sales order confirmed successfully'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """Mark a sales order as shipped."""
        order = self.get_object()
        if order.status != 'confirmed':
            return Response(
                {'error': 'Only confirmed orders can be shipped'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'shipped'
        order.shipped_at = timezone.now()
        order.save()
        
        return Response(
            {'message': 'Sales order marked as shipped'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        """Mark a sales order as delivered."""
        order = self.get_object()
        if order.status != 'shipped':
            return Response(
                {'error': 'Only shipped orders can be marked as delivered'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'delivered'
        order.delivered_at = timezone.now()
        order.save()
        
        return Response(
            {'message': 'Sales order marked as delivered'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a sales order."""
        order = self.get_object()
        if order.status in ['delivered', 'cancelled']:
            return Response(
                {'error': 'Cannot cancel delivered or already cancelled orders'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.cancelled_at = timezone.now()
        order.save()
        
        return Response(
            {'message': 'Sales order cancelled successfully'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get sales order analytics."""
        queryset = self.get_queryset()
        
        # Basic counts
        total_orders = queryset.count()
        pending_orders = queryset.filter(status='pending').count()
        confirmed_orders = queryset.filter(status='confirmed').count()
        shipped_orders = queryset.filter(status='shipped').count()
        delivered_orders = queryset.filter(status='delivered').count()
        cancelled_orders = queryset.filter(status='cancelled').count()
        
        # Financial analytics
        total_revenue = queryset.aggregate(total=Sum('total_amount'))['total'] or 0
        avg_order_value = queryset.aggregate(avg=Avg('total_amount'))['avg'] or 0
        
        # Time-based analytics
        today = timezone.now().date()
        this_month = queryset.filter(order_date__month=today.month, order_date__year=today.year)
        monthly_revenue = this_month.aggregate(total=Sum('total_amount'))['total'] or 0
        
        analytics_data = {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'confirmed_orders': confirmed_orders,
            'shipped_orders': shipped_orders,
            'delivered_orders': delivered_orders,
            'cancelled_orders': cancelled_orders,
            'total_revenue': total_revenue,
            'average_order_value': avg_order_value,
            'monthly_revenue': monthly_revenue,
            'monthly_orders': this_month.count()
        }
        
        return Response(analytics_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def revenue_trends(self, request):
        """Get revenue trends over time."""
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        queryset = self.get_queryset().filter(
            order_date__range=[start_date, end_date],
            status__in=['confirmed', 'shipped', 'delivered']
        )
        
        # Group by date and calculate daily revenue
        daily_revenue = []
        current_date = start_date
        
        while current_date <= end_date:
            day_orders = queryset.filter(order_date=current_date)
            day_revenue = day_orders.aggregate(total=Sum('total_amount'))['total'] or 0
            daily_revenue.append({
                'date': current_date.isoformat(),
                'revenue': day_revenue,
                'orders': day_orders.count()
            })
            current_date += timedelta(days=1)
        
        return Response({
            'period_days': days,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'daily_data': daily_revenue
        }, status=status.HTTP_200_OK)
