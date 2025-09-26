# Backend - Python Microservices

## 🐍 Technology Stack

- **Framework**: Django (primary) / Flask (microservices)
- **API**: Django REST Framework / FastAPI
- **Database**: PostgreSQL via Supabase
- **AI/ML**: Pandas, Scikit-learn, PyTorch/TensorFlow
- **Authentication**: Supabase JWT verification
- **Deployment**: Docker + Kubernetes, GitHub Actions
- **Monitoring**: Prometheus, Grafana, Sentry

## 📁 Architecture

```
backend/
├── api/                      # Main API service (Django/Flask)
│   ├── apps/
│   │   ├── auth/             # Authentication & user management
│   │   ├── inventory/        # Inventory management APIs
│   │   ├── analytics/        # Analytics and reporting APIs
│   │   └── core/             # Core utilities and models
│   ├── settings/             # Environment configurations
│   ├── requirements.txt      # Dependencies
│   └── Dockerfile           # Container configuration
├── ai_services/              # AI/ML microservices
│   ├── forecasting/          # Supply chain forecasting service
│   │   ├── models/           # ML model implementations
│   │   ├── api.py            # FastAPI service endpoints
│   │   ├── requirements.txt  # Service-specific dependencies
│   │   └── Dockerfile        # Service container
│   ├── risk_scoring/         # Risk assessment service
│   │   ├── scoring_engine.py # Risk calculation algorithms
│   │   ├── api.py            # FastAPI service endpoints
│   │   ├── requirements.txt  # Service-specific dependencies
│   │   └── Dockerfile        # Service container
│   └── copilot/              # Chat copilot with RAG
│       ├── rag_engine.py     # Retrieval-Augmented Generation
│       ├── embeddings.py     # Vector embedding generation
│       ├── api.py            # FastAPI service endpoints
│       ├── requirements.txt  # Service-specific dependencies
│       └── Dockerfile        # Service container
├── shared/                   # Shared utilities and models
│   ├── database/             # Database utilities and ORM models
│   ├── auth/                 # Shared authentication utilities
│   ├── utils/                # Common utility functions
│   └── types/                # Shared type definitions
├── docker-compose.yml        # Local development environment
└── requirements.txt          # Global Python dependencies
```

## 🔧 Core Services

### 1. Main API Service (Django/Flask)
**Endpoints**: `/api/v1/`
- **Inventory Management**: CRUD operations for stock levels, products, suppliers
- **Order Processing**: Purchase orders, shipments, tracking
- **User Management**: Profile management, preferences
- **Data Export**: CSV, Excel, PDF report generation
- **ERP Integration**: SAP, Odoo, MS Dynamics, NetSuite connectors

### 2. AI Forecasting Service
**Endpoints**: `/ai/forecast/`
- **Demand Forecasting**: Time series analysis using ARIMA, LSTM models
- **Supply Prediction**: Supplier reliability and delivery time forecasting
- **Inventory Optimization**: Optimal stock level recommendations
- **Seasonal Analysis**: Pattern recognition for seasonal variations

### 3. Risk Scoring Service
**Endpoints**: `/ai/risk/`
- **Supplier Risk Assessment**: Financial, operational, geographical risk scoring
- **Disruption Prediction**: Early warning system for supply chain disruptions
- **Compliance Monitoring**: Regulatory and quality compliance tracking
- **Market Risk Analysis**: Price volatility and market trend analysis

### 4. AI Copilot Service
**Endpoints**: `/ai/copilot/`
- **Conversational AI**: Natural language query processing
- **RAG Implementation**: Context-aware responses using vector database
- **Document Q&A**: Query uploaded documents (contracts, reports, manuals)
- **Action Suggestions**: Proactive recommendations based on data analysis

## 📊 Supabase Integration

### Database Connection:
```python
# Using supabase-py client
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

# Direct PostgreSQL connection (Django ORM)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('SUPABASE_DB_NAME'),
        'USER': os.environ.get('SUPABASE_DB_USER'),
        'PASSWORD': os.environ.get('SUPABASE_DB_PASSWORD'),
        'HOST': os.environ.get('SUPABASE_DB_HOST'),
        'PORT': os.environ.get('SUPABASE_DB_PORT', '5432'),
    }
}
```

### Authentication:
- **JWT Verification**: Validate Supabase JWTs in API middleware
- **Role-Level Security**: Implement RLS policies at application level
- **User Context**: Extract user information from JWT for data filtering

### Real-time Features:
- **WebSocket Integration**: Real-time updates for dashboard metrics
- **Event Publishing**: Publish data changes to Supabase Realtime
- **Notification System**: Alert users of important events

## 🤖 AI/ML Implementation

### Model Training Pipeline:
1. **Data Extraction**: Pull historical data from Supabase
2. **Feature Engineering**: Create relevant features for ML models
3. **Model Training**: Train and validate models using scikit-learn/PyTorch
4. **Model Deployment**: Containerize models for production serving
5. **Performance Monitoring**: Track model accuracy and drift detection

### Vector Database (RAG):
- **Embedding Generation**: Use OpenAI/HuggingFace models for text embedding
- **Vector Storage**: Store embeddings in Supabase with pg_vector extension
- **Similarity Search**: Implement semantic search for document retrieval
- **Context Assembly**: Combine retrieved context with user queries

## 🔄 Development Workflow

### Local Development:
```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver

# Or use Docker Compose
docker-compose up -d
```

### Testing:
```bash
# Run unit tests
pytest

# Run integration tests
pytest tests/integration/

# Test with coverage
pytest --cov=.

# Test specific service
pytest ai_services/forecasting/tests/
```

### API Testing:
- **Postman Collections**: Comprehensive API testing suites
- **Automated Testing**: CI/CD pipeline runs all tests on PR
- **Load Testing**: Performance testing with Locust
- **Security Testing**: OWASP ZAP integration

## 🔐 Security & Authentication

### JWT Validation Middleware:
```python
import jwt
from django.conf import settings
from supabase import create_client

def authenticate_supabase_user(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    try:
        decoded = jwt.decode(token, settings.SUPABASE_JWT_SECRET, algorithms=['HS256'])
        user_id = decoded.get('sub')
        return user_id
    except jwt.InvalidTokenError:
        raise PermissionDenied('Invalid token')
```

### Environment Variables:
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Public API key
- `SUPABASE_SERVICE_KEY`: Service role key (backend only)
- `SUPABASE_JWT_SECRET`: JWT signing secret
- `DATABASE_URL`: PostgreSQL connection string

## 📦 Deployment

### Docker Configuration:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:application"]
```

### Kubernetes Deployment:
- **Service Mesh**: Istio for traffic management
- **Auto Scaling**: HPA based on CPU/memory usage
- **Health Checks**: Liveness and readiness probes
- **Secret Management**: Kubernetes secrets for environment variables

### CI/CD Pipeline:
- **GitHub Actions**: Automated testing, building, and deployment
- **Container Registry**: Docker Hub/AWS ECR for image storage
- **Environment Promotion**: Dev → Staging → Production pipeline
- **Rollback Strategy**: Blue-green deployment for zero-downtime updates

## 📊 Monitoring & Observability

- **Application Metrics**: Prometheus + Grafana dashboards
- **Error Tracking**: Sentry integration for error monitoring
- **Log Aggregation**: ELK stack or CloudWatch for log management
- **Performance Monitoring**: APM tools for request tracing
- **Health Checks**: Automated monitoring and alerting

---

**Next Steps**:
1. Set up Django project structure
2. Implement Supabase authentication middleware
3. Create core API endpoints
4. Develop AI microservices
5. Set up Docker containers and CI/CD pipeline
