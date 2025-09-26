-- SupplyMind AI Platform RLS Policies
-- Row Level Security policies for multi-tenant data access

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.order_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.shipments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.risk_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analytics_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_base ENABLE ROW LEVEL SECURITY;

-- Helper function to get current user's company_id
CREATE OR REPLACE FUNCTION get_user_company_id()
RETURNS UUID AS $$
BEGIN
  RETURN (
    SELECT company_id 
    FROM public.users 
    WHERE id = auth.uid()
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper function to check if user is admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
  RETURN (
    SELECT role = 'admin' 
    FROM public.users 
    WHERE id = auth.uid()
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Users table policies
CREATE POLICY "Users can view own profile" 
  ON public.users FOR SELECT 
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" 
  ON public.users FOR UPDATE 
  USING (auth.uid() = id);

CREATE POLICY "Users can view company members" 
  ON public.users FOR SELECT 
  USING (company_id = get_user_company_id());

CREATE POLICY "Admins can manage all company users" 
  ON public.users FOR ALL 
  USING (is_admin() AND company_id = get_user_company_id());

-- Companies table policies
CREATE POLICY "Users can view own company" 
  ON public.companies FOR SELECT 
  USING (id = get_user_company_id());

CREATE POLICY "Admins can update own company" 
  ON public.companies FOR UPDATE 
  USING (is_admin() AND id = get_user_company_id());

-- Suppliers table policies
CREATE POLICY "Users can view company suppliers" 
  ON public.suppliers FOR SELECT 
  USING (company_id = get_user_company_id());

CREATE POLICY "Managers can manage company suppliers" 
  ON public.suppliers FOR ALL 
  USING (
    company_id = get_user_company_id() AND 
    (SELECT role FROM public.users WHERE id = auth.uid()) IN ('admin', 'manager')
  );

-- Inventory table policies
CREATE POLICY "Users can view company inventory" 
  ON public.inventory FOR SELECT 
  USING (company_id = get_user_company_id());

CREATE POLICY "Managers can manage company inventory" 
  ON public.inventory FOR ALL 
  USING (
    company_id = get_user_company_id() AND 
    (SELECT role FROM public.users WHERE id = auth.uid()) IN ('admin', 'manager')
  );

-- Orders table policies
CREATE POLICY "Users can view company orders" 
  ON public.orders FOR SELECT 
  USING (company_id = get_user_company_id());

CREATE POLICY "Managers can manage company orders" 
  ON public.orders FOR ALL 
  USING (
    company_id = get_user_company_id() AND 
    (SELECT role FROM public.users WHERE id = auth.uid()) IN ('admin', 'manager')
  );

-- Order Items table policies
CREATE POLICY "Users can view company order items" 
  ON public.order_items FOR SELECT 
  USING (
    EXISTS (
      SELECT 1 FROM public.orders 
      WHERE id = order_id 
      AND company_id = get_user_company_id()
    )
  );

CREATE POLICY "Managers can manage company order items" 
  ON public.order_items FOR ALL 
  USING (
    EXISTS (
      SELECT 1 FROM public.orders 
      WHERE id = order_id 
      AND company_id = get_user_company_id()
    ) AND 
    (SELECT role FROM public.users WHERE id = auth.uid()) IN ('admin', 'manager')
  );

-- Shipments table policies
CREATE POLICY "Users can view company shipments" 
  ON public.shipments FOR SELECT 
  USING (company_id = get_user_company_id());

CREATE POLICY "Managers can manage company shipments" 
  ON public.shipments FOR ALL 
  USING (
    company_id = get_user_company_id() AND 
    (SELECT role FROM public.users WHERE id = auth.uid()) IN ('admin', 'manager')
  );

-- Risk Assessments table policies
CREATE POLICY "Users can view company risk assessments" 
  ON public.risk_assessments FOR SELECT 
  USING (company_id = get_user_company_id());

CREATE POLICY "Analysts can manage company risk assessments" 
  ON public.risk_assessments FOR ALL 
  USING (
    company_id = get_user_company_id() AND 
    (SELECT role FROM public.users WHERE id = auth.uid()) IN ('admin', 'manager', 'analyst')
  );

-- Analytics Events table policies
CREATE POLICY "Users can view company analytics" 
  ON public.analytics_events FOR SELECT 
  USING (company_id = get_user_company_id());

CREATE POLICY "System can insert analytics events" 
  ON public.analytics_events FOR INSERT 
  WITH CHECK (company_id = get_user_company_id());

CREATE POLICY "Admins can manage company analytics" 
  ON public.analytics_events FOR ALL 
  USING (
    company_id = get_user_company_id() AND 
    (SELECT role FROM public.users WHERE id = auth.uid()) = 'admin'
  );

-- Knowledge Base table policies
CREATE POLICY "Users can view company knowledge base" 
  ON public.knowledge_base FOR SELECT 
  USING (company_id = get_user_company_id());

CREATE POLICY "Managers can manage company knowledge base" 
  ON public.knowledge_base FOR ALL 
  USING (
    company_id = get_user_company_id() AND 
    (SELECT role FROM public.users WHERE id = auth.uid()) IN ('admin', 'manager')
  );

-- Special policy for user registration (handled by trigger)
CREATE POLICY "Enable insert for authenticated users during registration" 
  ON public.users FOR INSERT 
  WITH CHECK (auth.uid() = id);

-- Grant usage on custom functions
GRANT EXECUTE ON FUNCTION get_user_company_id() TO authenticated;
GRANT EXECUTE ON FUNCTION is_admin() TO authenticated;
GRANT EXECUTE ON FUNCTION update_updated_at_column() TO authenticated;
