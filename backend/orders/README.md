# Orders Management REST API

Comprehensive Django REST API implementation for managing Purchase Orders and Sales Orders with full CRUD operations, advanced filtering, and analytics integration.

## Features

### 🚀 Core Functionality
- **Full CRUD Operations** for both Purchase Orders and Sales Orders
- **Advanced Filtering** with multiple criteria and search capabilities
- **Analytics Integration** with comprehensive reporting endpoints
- **Status Management** with workflow-based order transitions
- **Data Validation** with robust serializers and custom validation rules
- **Testable Endpoints** designed for comprehensive API testing

### 📊 Order Types

#### Purchase Orders
- Create, read, update, delete purchase orders
- Approve/cancel/mark delivered workflows
- Supplier-based filtering and management
- Purchase analytics and reporting

#### Sales Orders
- Create, read, update, delete sales orders
- Confirm/ship/deliver/cancel workflows
- Customer-based filtering and management
- Revenue analytics and trend reporting

## API Endpoints

### Purchase Orders
```
GET    /api/purchase-orders/                    - List all purchase orders
POST   /api/purchase-orders/                    - Create new purchase order  
GET    /api/purchase-orders/{id}/               - Get specific purchase order
PUT    /api/purchase-orders/{id}/               - Update purchase order
PATCH  /api/purchase-orders/{id}/               - Partial update purchase order
DELETE /api/purchase-orders/{id}/               - Delete purchase order
POST   /api/purchase-orders/{id}/approve/       - Approve purchase order
POST   /api/purchase-orders/{id}/cancel/        - Cancel purchase order
POST   /api/purchase-orders/{id}/mark-delivered/ - Mark as delivered
GET    /api/purchase-orders/analytics/          - Get purchase order analytics
```

### Sales Orders
```
GET    /api/sales-orders/                       - List all sales orders
POST   /api/sales-orders/                       - Create new sales order
GET    /api/sales-orders/{id}/                  - Get specific sales order
PUT    /api/sales-orders/{id}/                  - Update sales order
PATCH  /api/sales-orders/{id}/                  - Partial update sales order
DELETE /api/sales-orders/{id}/                  - Delete sales order
POST   /api/sales-orders/{id}/confirm/          - Confirm sales order
POST   /api/sales-orders/{id}/ship/             - Mark as shipped
POST   /api/sales-orders/{id}/deliver/          - Mark as delivered
POST   /api/sales-orders/{id}/cancel/           - Cancel sales order
GET    /api/sales-orders/analytics/             - Get sales order analytics
GET    /api/sales-orders/revenue-trends/        - Get revenue trends
```

## Advanced Filtering

### Query Parameters
- **status**: Filter by order status
- **start_date, end_date**: Date range filtering
- **supplier_id / customer_id**: Filter by supplier/customer
- **search**: Global text search across multiple fields
- **min_amount, max_amount**: Amount range filtering
- **ordering**: Sort results (e.g., -created_at, total_amount)
- **page, page_size**: Pagination support
- **is_approved, is_confirmed**: Boolean status filters
- **is_overdue**: Filter overdue orders
- **has_items**: Filter orders with/without items

### Advanced Filter Examples
```
/api/purchase-orders/?status=pending&min_amount=1000&ordering=-created_at
/api/sales-orders/?customer_name=Smith&start_date=2024-01-01&is_overdue=true
/api/purchase-orders/?search=urgent&status_in=pending,approved
```

## Analytics Endpoints

### Purchase Order Analytics
```json
{
  "total_orders": 150,
  "pending_orders": 25,
  "approved_orders": 100,
  "delivered_orders": 20,
  "cancelled_orders": 5,
  "total_value": 50000.00,
  "average_order_value": 333.33,
  "monthly_value": 15000.00,
  "monthly_orders": 45
}
```

### Sales Order Analytics
```json
{
  "total_orders": 200,
  "pending_orders": 30,
  "confirmed_orders": 120,
  "shipped_orders": 40,
  "delivered_orders": 8,
  "cancelled_orders": 2,
  "total_revenue": 75000.00,
  "average_order_value": 375.00,
  "monthly_revenue": 22500.00,
  "monthly_orders": 60
}
```

### Revenue Trends
```json
{
  "period_days": 30,
  "start_date": "2024-01-01",
  "end_date": "2024-01-30",
  "daily_data": [
    {
      "date": "2024-01-01",
      "revenue": 1500.00,
      "orders": 4
    }
  ]
}
```

## File Structure

```
orders/
├── __init__.py              # App initialization
├── apps.py                  # Django app configuration
├── views.py                 # REST API viewsets with CRUD and analytics
├── serializers.py           # DRF serializers with validation
├── filters.py               # Advanced filtering capabilities
├── urls.py                  # URL routing configuration
└── README.md               # This documentation
```

## Key Features

### 🔐 Authentication & Permissions
- All endpoints require authentication
- User-based order creation tracking
- Permission-based access control

### 🛡️ Data Validation
- Comprehensive input validation
- Business rule enforcement
- Error handling with descriptive messages

### 📈 Analytics Integration
- Real-time order statistics
- Revenue tracking and trends
- Performance metrics
- Time-based analytics

### 🔍 Advanced Search & Filtering
- Multi-field global search
- Status-based filtering
- Date range filtering
- Amount range filtering
- Supplier/Customer filtering
- Boolean condition filtering

### 🔄 Order Workflow Management
- Status transition validation
- Workflow-based state changes
- Audit trail tracking
- User action logging

## Testing

The API is designed with comprehensive testing in mind:

- All endpoints support standard HTTP methods
- Proper error codes and messages
- Validation error responses
- Analytics endpoint testing
- Workflow transition testing

## Integration

This orders app integrates seamlessly with:
- **shared/models.py** for PurchaseOrder and SalesOrder models
- Django REST Framework for API functionality
- Django Filter for advanced filtering
- Authentication system for user management
- Analytics backend for reporting
