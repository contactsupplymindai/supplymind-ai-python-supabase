# Supabase Configuration & Database Management

## 📦 Overview

This folder contains all Supabase-related configuration, database migrations, and setup files for the SupplyMind AI Platform. Supabase serves as our unified Backend-as-a-Service (BaaS) platform providing PostgreSQL database, authentication, real-time subscriptions, file storage, and vector embeddings.

## 📁 Structure

```
supabase/
├── config.toml              # Supabase CLI configuration
├── migrations/              # Database schema migrations
│   ├── 00000000000000_init.sql  # Initial schema
│   ├── 20240101000000_inventory.sql  # Inventory tables
│   ├── 20240101000001_orders.sql     # Order management tables
│   ├── 20240101000002_analytics.sql  # Analytics and reporting
│   ├── 20240101000003_ai_models.sql  # AI model results storage
│   └── 20240101000004_vector_store.sql # Vector embeddings for RAG
├── seed.sql                 # Initial data seeding
├── functions/               # PostgreSQL functions and triggers
│   ├── risk_calculation.sql     # Risk scoring functions
│   └── inventory_triggers.sql   # Inventory update triggers
├── policies/                # Row Level Security (RLS) policies
│   ├── inventory_policies.sql   # Inventory data access policies
│   ├── user_policies.sql        # User data access policies
│   └── analytics_policies.sql   # Analytics data access policies
└── types/                   # Custom PostgreSQL types
    ├── enums.sql                # Enumeration types
    └── composite_types.sql      # Composite data types
```

## 🔧 Core Features

### Database (PostgreSQL)
- **Core Tables**: Inventory, Orders, Shipments, Suppliers, RiskEvents
- **Analytics Tables**: Forecasting results, risk scores, KPI metrics
- **Vector Storage**: pg_vector extension for AI embeddings
- **Full-text Search**: PostgreSQL text search capabilities
- **JSON Support**: Advanced JSON operations for flexible data storage

### Authentication (Supabase Auth)
- **Multi-provider Auth**: Email, Google, GitHub, SSO integration
- **JWT Tokens**: Secure token-based authentication
- **User Management**: Profile management and role assignment
- **Row Level Security**: Database-level access control

### Real-time (Supabase Realtime)
- **Live Updates**: Real-time dashboard KPI updates
- **Collaboration**: Live chat and notification system
- **Data Subscriptions**: Automatic UI updates on data changes
- **WebSocket Management**: Efficient real-time connections

### Storage (Supabase Storage)
- **Document Storage**: Supplier certificates, invoices, reports
- **File Organization**: Bucket-based organization with access policies
- **CDN Integration**: Global file delivery network
- **Security**: Role-based file access permissions

### Vector Database (pg_vector)
- **Embedding Storage**: Vector embeddings for documents and data
- **Similarity Search**: Semantic search capabilities for AI Copilot
- **RAG Support**: Retrieval-Augmented Generation for chat features
- **Performance**: Optimized indexing for fast vector queries

## 🔐 Security & Access Control

### Row Level Security (RLS) Policies
```sql
-- Example: Inventory access policy
CREATE POLICY "inventory_access_policy" ON inventory
  FOR ALL USING (
    auth.uid() IN (
      SELECT user_id FROM user_permissions 
      WHERE resource_type = 'inventory' 
      AND permission_level >= 'read'
    )
  );

-- User can only access their own data
CREATE POLICY "user_data_policy" ON user_profiles
  FOR ALL USING (auth.uid() = id);
```

### Role-Based Access
- **Admin**: Full access to all resources
- **Manager**: Access to team resources and analytics
- **Analyst**: Read access to analytics and reporting
- **Operator**: Limited access to operational data
- **Viewer**: Read-only access to dashboards

## 🚀 Development Setup

### Prerequisites
```bash
# Install Supabase CLI
npm install -g supabase
# or
brew install supabase/tap/supabase

# Verify installation
supabase --version
```

### Local Development
```bash
# Start local Supabase instance
supabase start

# Apply migrations
supabase db reset

# Generate TypeScript types
supabase gen types typescript --local > ../frontend/src/types/database.types.ts

# View local dashboard
# Navigate to: http://localhost:54323
```

### Database Migrations
```bash
# Create new migration
supabase migration new add_new_feature

# Apply migrations locally
supabase db reset

# Deploy to staging
supabase db push --project-ref <staging-ref>

# Deploy to production
supabase db push --project-ref <production-ref>
```

## 📊 Database Schema

### Core Tables

#### Inventory Management
```sql
CREATE TABLE inventory (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  product_id VARCHAR NOT NULL,
  product_name VARCHAR NOT NULL,
  category VARCHAR NOT NULL,
  current_stock INTEGER NOT NULL DEFAULT 0,
  min_stock_level INTEGER NOT NULL DEFAULT 0,
  max_stock_level INTEGER NOT NULL DEFAULT 1000,
  unit_cost DECIMAL(10,2),
  supplier_id UUID REFERENCES suppliers(id),
  location VARCHAR,
  last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Supply Chain Analytics
```sql
CREATE TABLE forecast_results (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  product_id VARCHAR NOT NULL,
  forecast_date DATE NOT NULL,
  predicted_demand INTEGER NOT NULL,
  confidence_interval DECIMAL(5,2),
  model_version VARCHAR,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE risk_scores (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  entity_type VARCHAR NOT NULL, -- 'supplier', 'product', 'route'
  entity_id UUID NOT NULL,
  risk_category VARCHAR NOT NULL,
  risk_score DECIMAL(5,2) NOT NULL,
  risk_factors JSONB,
  calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Vector Embeddings for AI
```sql
-- Enable pg_vector extension
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE document_embeddings (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  document_id UUID NOT NULL,
  document_type VARCHAR NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536), -- OpenAI embedding dimension
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create vector index for similarity search
CREATE INDEX ON document_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

## 🤖 AI Integration

### Vector Search Functions
```sql
-- Function for similarity search (RAG)
CREATE OR REPLACE FUNCTION search_documents(
  query_embedding vector(1536),
  match_threshold float DEFAULT 0.7,
  match_count int DEFAULT 5
)
RETURNS TABLE (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    document_embeddings.id,
    document_embeddings.content,
    document_embeddings.metadata,
    1 - (document_embeddings.embedding <=> query_embedding) AS similarity
  FROM document_embeddings
  WHERE 1 - (document_embeddings.embedding <=> query_embedding) > match_threshold
  ORDER BY document_embeddings.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
```

## 🔄 CI/CD Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/supabase.yml
name: Deploy Supabase Migrations

on:
  push:
    branches: [main]
    paths: ['supabase/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Supabase CLI
        uses: supabase/setup-cli@v1
        
      - name: Deploy migrations to staging
        run: supabase db push --project-ref ${{ secrets.SUPABASE_STAGING_REF }}
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
          
      - name: Deploy migrations to production
        if: github.ref == 'refs/heads/main'
        run: supabase db push --project-ref ${{ secrets.SUPABASE_PROD_REF }}
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
```

### Environment Variables
```bash
# Required GitHub Secrets
SUPABASE_ACCESS_TOKEN=your_supabase_access_token
SUPABASE_STAGING_REF=your_staging_project_ref
SUPABASE_PROD_REF=your_production_project_ref

# Application Environment Variables
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key
SUPABASE_JWT_SECRET=your_jwt_secret
```

## 📊 Monitoring & Performance

### Database Performance
- **Connection Pooling**: PgBouncer for efficient connections
- **Query Optimization**: Regular EXPLAIN ANALYZE for slow queries
- **Index Management**: Proper indexing for frequently queried columns
- **Vacuum Strategy**: Automated maintenance tasks

### Real-time Performance
- **Connection Limits**: Monitor concurrent real-time connections
- **Message Rate**: Track real-time message throughput
- **Subscription Management**: Optimize subscription patterns

### Storage Monitoring
- **Storage Usage**: Monitor file storage consumption
- **Bandwidth Tracking**: CDN usage and transfer rates
- **Access Patterns**: Analyze file access patterns for optimization

## 🗺 Backup & Recovery

### Automated Backups
- **Daily Backups**: Automated daily database snapshots
- **Point-in-Time Recovery**: 7-day recovery window
- **Cross-Region Replication**: Production data replication

### Disaster Recovery
- **Backup Restoration**: Procedure for database restoration
- **Failover Strategy**: Multi-region failover capabilities
- **Data Integrity**: Regular backup validation processes

---

## 🚀 Quick Start Commands

```bash
# Initialize Supabase in existing project
supabase init

# Start local development environment
supabase start

# Create and apply a new migration
supabase migration new your_migration_name
supabase db reset

# Generate TypeScript types
supabase gen types typescript --local > types/database.types.ts

# Deploy to production
supabase db push --project-ref your-project-ref

# Stop local environment
supabase stop
```

## 📚 Resources

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [pg_vector Extension](https://github.com/pgvector/pgvector)
- [Supabase CLI Reference](https://supabase.com/docs/reference/cli)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)

---

**Next Steps**:
1. Set up Supabase project on supabase.com
2. Configure environment variables
3. Run initial database migrations
4. Set up Row Level Security policies
5. Configure CI/CD for automated deployments
