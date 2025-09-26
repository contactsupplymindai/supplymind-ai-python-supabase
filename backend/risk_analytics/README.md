# Risk Analytics API

A comprehensive Django REST API for supply chain risk management, anomaly detection, and analytics.

## Overview

This microservice provides endpoints for:
- Risk event creation and management
- Risk scoring and updates
- Anomaly detection
- Supplier KPI tracking
- Analytics and reporting

## API Endpoints

### Base URL
```
/api/v1/
```

### Risk Events

#### Standard CRUD Operations
- `GET /risk-events/` - List all risk events
- `POST /risk-events/` - Create a new risk event
- `GET /risk-events/{id}/` - Retrieve specific risk event
- `PUT /risk-events/{id}/` - Update risk event
- `PATCH /risk-events/{id}/` - Partial update risk event
- `DELETE /risk-events/{id}/` - Delete risk event

#### Custom Operations
- `POST /risk-events/{id}/score/` - Calculate risk score for event
- `POST /risk-events/bulk-create/` - Bulk create risk events

### Risk Scores

#### Standard CRUD Operations
- `GET /risk-scores/` - List all risk scores
- `POST /risk-scores/` - Create a new risk score
- `GET /risk-scores/{id}/` - Retrieve specific risk score
- `PUT /risk-scores/{id}/` - Update risk score
- `PATCH /risk-scores/{id}/` - Partial update risk score
- `DELETE /risk-scores/{id}/` - Delete risk score

#### Custom Operations
- `POST /risk-scores/bulk-update/` - Bulk update risk scores

### Anomaly Detection

#### Standard CRUD Operations
- `GET /anomalies/` - List all anomalies
- `POST /anomalies/` - Create a new anomaly
- `GET /anomalies/{id}/` - Retrieve specific anomaly
- `PUT /anomalies/{id}/` - Update anomaly
- `PATCH /anomalies/{id}/` - Partial update anomaly
- `DELETE /anomalies/{id}/` - Delete anomaly

#### Custom Operations
- `POST /anomalies/detect/` - Run anomaly detection
- `GET /anomalies/by-supplier/{supplier_id}/` - Get anomalies for specific supplier

### Supplier KPIs

#### Standard CRUD Operations
- `GET /supplier-kpis/` - List all KPIs
- `POST /supplier-kpis/` - Create a new KPI
- `GET /supplier-kpis/{id}/` - Retrieve specific KPI
- `PUT /supplier-kpis/{id}/` - Update KPI
- `PATCH /supplier-kpis/{id}/` - Partial update KPI
- `DELETE /supplier-kpis/{id}/` - Delete KPI

### Analytics Endpoints

- `GET /suppliers/{supplier_id}/risk-summary/` - Get risk summary for supplier
- `GET /analytics/risk-trends/` - Risk trends over time
- `GET /analytics/anomaly-trends/` - Anomaly trends over time
- `GET /analytics/kpi-trends/` - KPI trends over time
- `GET /analytics/dashboard/` - Dashboard analytics data

## Request/Response Examples

### Create Risk Event

```json
POST /api/v1/risk-events/
{
    "supplier_id": 123,
    "event_type": "QUALITY_ISSUE",
    "severity": "HIGH",
    "description": "Quality control failure detected",
    "impact_score": 8.5,
    "probability": 0.75,
    "mitigation_plan": "Increase quality inspections"
}
```

### Risk Score Response

```json
{
    "id": 1,
    "risk_event": 123,
    "score": 85.5,
    "confidence_level": 0.92,
    "scoring_method": "ML_ALGORITHM",
    "factors": {
        "severity": 8.5,
        "probability": 0.75,
        "historical_impact": 7.2
    },
    "created_at": "2025-09-26T15:30:00Z",
    "updated_at": "2025-09-26T15:30:00Z"
}
```

### Anomaly Detection Request

```json
POST /api/v1/anomalies/detect/
{
    "supplier_id": 123,
    "time_range": {
        "start_date": "2025-09-01",
        "end_date": "2025-09-26"
    },
    "detection_parameters": {
        "threshold": 0.05,
        "algorithm": "ISOLATION_FOREST"
    }
}
```

### Analytics Dashboard Response

```json
{
    "risk_summary": {
        "total_events": 45,
        "high_risk_events": 12,
        "average_score": 6.3
    },
    "anomaly_summary": {
        "total_anomalies": 8,
        "new_anomalies_today": 2,
        "critical_anomalies": 1
    },
    "kpi_summary": {
        "delivery_performance": 95.2,
        "quality_score": 88.7,
        "cost_efficiency": 92.1
    },
    "trends": {
        "risk_trend": "DECREASING",
        "anomaly_trend": "STABLE",
        "kpi_trend": "IMPROVING"
    }
}
```

## Query Parameters

### Filtering
- `supplier_id` - Filter by supplier ID
- `event_type` - Filter by event type
- `severity` - Filter by severity level
- `date_from` - Filter events from date
- `date_to` - Filter events to date
- `status` - Filter by status

### Pagination
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

### Sorting
- `ordering` - Sort by field (prefix with `-` for descending)
  - Examples: `created_at`, `-severity`, `score`

## Authentication

All endpoints require authentication. Include the authorization header:

```
Authorization: Bearer <your-token>
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "Invalid request data",
    "details": {
        "field_name": ["This field is required"]
    }
}
```

### 404 Not Found
```json
{
    "error": "Resource not found",
    "message": "Risk event with id 999 does not exist"
}
```

### 500 Internal Server Error
```json
{
    "error": "Internal server error",
    "message": "An unexpected error occurred"
}
```

## Rate Limiting

- Standard endpoints: 1000 requests per hour
- Analytics endpoints: 100 requests per hour
- Bulk operations: 10 requests per hour

## Data Models

### RiskEvent
- `id`: Primary key
- `supplier_id`: Foreign key to supplier
- `event_type`: Type of risk event
- `severity`: Risk severity level
- `description`: Event description
- `impact_score`: Numerical impact assessment
- `probability`: Probability of occurrence
- `mitigation_plan`: Planned mitigation actions
- `status`: Current status
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### RiskScore
- `id`: Primary key
- `risk_event`: Foreign key to risk event
- `score`: Calculated risk score
- `confidence_level`: Confidence in score
- `scoring_method`: Method used for scoring
- `factors`: JSON field with scoring factors
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Anomaly
- `id`: Primary key
- `supplier_id`: Foreign key to supplier
- `anomaly_type`: Type of anomaly
- `severity`: Anomaly severity
- `description`: Anomaly description
- `detected_at`: Detection timestamp
- `confidence_score`: Detection confidence
- `parameters`: Detection parameters used
- `status`: Investigation status
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### SupplierKPI
- `id`: Primary key
- `supplier_id`: Foreign key to supplier
- `kpi_type`: Type of KPI
- `value`: KPI value
- `target_value`: Target value
- `unit`: Unit of measurement
- `measurement_date`: Date of measurement
- `performance_rating`: Calculated rating
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Installation & Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Start the server:
```bash
python manage.py runserver
```

## Testing

Run tests with:
```bash
python manage.py test risk_analytics
```

## Contributing

1. Follow PEP 8 style guidelines
2. Write comprehensive tests
3. Update documentation for new endpoints
4. Use semantic commit messages

## License

Proprietary - SupplyMind AI
