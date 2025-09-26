-- SupplyMind AI Platform Database Functions
-- Custom functions for AI operations, analytics, and business logic

-- Function to calculate inventory risk score
CREATE OR REPLACE FUNCTION calculate_inventory_risk(
  current_stock INTEGER,
  min_stock INTEGER,
  max_stock INTEGER,
  demand_volatility DECIMAL DEFAULT 0.0
) RETURNS DECIMAL AS $$
DECLARE
  stock_ratio DECIMAL;
  risk_score DECIMAL;
BEGIN
  -- Calculate stock ratio (current vs minimum)
  IF min_stock = 0 THEN
    stock_ratio := 1.0;
  ELSE
    stock_ratio := current_stock::DECIMAL / min_stock::DECIMAL;
  END IF;
  
  -- Base risk calculation
  CASE 
    WHEN stock_ratio >= 2.0 THEN risk_score := 0.1;
    WHEN stock_ratio >= 1.5 THEN risk_score := 0.2;
    WHEN stock_ratio >= 1.0 THEN risk_score := 0.4;
    WHEN stock_ratio >= 0.5 THEN risk_score := 0.7;
    ELSE risk_score := 0.9;
  END CASE;
  
  -- Adjust for demand volatility
  risk_score := risk_score + (demand_volatility * 0.2);
  
  -- Ensure risk score is between 0 and 1
  RETURN LEAST(GREATEST(risk_score, 0.0), 1.0);
END;
$$ LANGUAGE plpgsql;

-- Function to calculate supplier performance score
CREATE OR REPLACE FUNCTION calculate_supplier_score(
  supplier_uuid UUID,
  period_days INTEGER DEFAULT 90
) RETURNS DECIMAL AS $$
DECLARE
  on_time_rate DECIMAL;
  quality_score DECIMAL;
  response_time DECIMAL;
  total_orders INTEGER;
  final_score DECIMAL;
BEGIN
  -- Get total orders in period
  SELECT COUNT(*) INTO total_orders
  FROM public.orders o
  WHERE o.supplier_id = supplier_uuid
    AND o.created_at >= NOW() - INTERVAL '1 day' * period_days;
  
  -- If no orders, return neutral score
  IF total_orders = 0 THEN
    RETURN 0.5;
  END IF;
  
  -- Calculate on-time delivery rate
  SELECT 
    COALESCE(
      COUNT(CASE WHEN actual_delivery <= expected_delivery THEN 1 END)::DECIMAL 
      / NULLIF(COUNT(*), 0),
      0.5
    ) INTO on_time_rate
  FROM public.orders o
  WHERE o.supplier_id = supplier_uuid
    AND o.created_at >= NOW() - INTERVAL '1 day' * period_days
    AND o.actual_delivery IS NOT NULL
    AND o.expected_delivery IS NOT NULL;
  
  -- Simple quality and response metrics (can be enhanced)
  quality_score := 0.8; -- Placeholder for quality metrics
  response_time := 0.7;  -- Placeholder for response time metrics
  
  -- Weighted final score
  final_score := (on_time_rate * 0.5) + (quality_score * 0.3) + (response_time * 0.2);
  
  RETURN LEAST(GREATEST(final_score, 0.0), 1.0);
END;
$$ LANGUAGE plpgsql;

-- Function for semantic similarity search in knowledge base
CREATE OR REPLACE FUNCTION search_knowledge_base(
  query_embedding vector(1536),
  company_uuid UUID,
  match_threshold DECIMAL DEFAULT 0.8,
  match_count INTEGER DEFAULT 10
) RETURNS TABLE (
  id UUID,
  title TEXT,
  content TEXT,
  similarity DECIMAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    kb.id,
    kb.title,
    kb.content,
    1 - (kb.embedding <=> query_embedding) AS similarity
  FROM public.knowledge_base kb
  WHERE kb.company_id = company_uuid
    AND 1 - (kb.embedding <=> query_embedding) > match_threshold
  ORDER BY kb.embedding <=> query_embedding
  LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- Function to update inventory status based on stock levels
CREATE OR REPLACE FUNCTION update_inventory_status()
RETURNS TRIGGER AS $$
BEGIN
  -- Update status based on current stock levels
  CASE 
    WHEN NEW.current_stock = 0 THEN 
      NEW.status := 'out_of_stock';
    WHEN NEW.current_stock <= NEW.min_stock_level THEN 
      NEW.status := 'low_stock';
    WHEN NEW.status = 'discontinued' THEN
      -- Keep discontinued status
      NEW.status := 'discontinued';
    ELSE 
      NEW.status := 'active';
  END CASE;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to automatically create risk assessments
CREATE OR REPLACE FUNCTION create_inventory_risk_assessment(
  inventory_uuid UUID
) RETURNS UUID AS $$
DECLARE
  risk_score DECIMAL;
  risk_level_val risk_level;
  assessment_id UUID;
  inventory_record RECORD;
BEGIN
  -- Get inventory details
  SELECT * INTO inventory_record
  FROM public.inventory
  WHERE id = inventory_uuid;
  
  -- Calculate risk score
  risk_score := calculate_inventory_risk(
    inventory_record.current_stock,
    inventory_record.min_stock_level,
    inventory_record.max_stock_level
  );
  
  -- Determine risk level
  CASE 
    WHEN risk_score >= 0.8 THEN risk_level_val := 'critical';
    WHEN risk_score >= 0.6 THEN risk_level_val := 'high';
    WHEN risk_score >= 0.4 THEN risk_level_val := 'medium';
    ELSE risk_level_val := 'low';
  END CASE;
  
  -- Create risk assessment
  INSERT INTO public.risk_assessments (
    company_id,
    inventory_id,
    risk_type,
    risk_level,
    score,
    factors,
    recommendations
  ) VALUES (
    inventory_record.company_id,
    inventory_uuid,
    'inventory_stock',
    risk_level_val,
    risk_score,
    jsonb_build_object(
      'current_stock', inventory_record.current_stock,
      'min_stock', inventory_record.min_stock_level,
      'stock_ratio', CASE WHEN inventory_record.min_stock_level > 0 
                     THEN inventory_record.current_stock::DECIMAL / inventory_record.min_stock_level::DECIMAL 
                     ELSE 1.0 END
    ),
    CASE 
      WHEN risk_level_val = 'critical' THEN 
        jsonb_build_array('Immediate restock required', 'Consider emergency procurement')
      WHEN risk_level_val = 'high' THEN 
        jsonb_build_array('Schedule urgent restock', 'Review supplier lead times')
      WHEN risk_level_val = 'medium' THEN 
        jsonb_build_array('Plan restock within 2 weeks', 'Monitor consumption rate')
      ELSE 
        jsonb_build_array('Stock levels adequate', 'Continue monitoring')
    END
  ) RETURNING id INTO assessment_id;
  
  RETURN assessment_id;
END;
$$ LANGUAGE plpgsql;

-- Function to log analytics events
CREATE OR REPLACE FUNCTION log_analytics_event(
  company_uuid UUID,
  user_uuid UUID,
  event_type_val TEXT,
  event_data_val JSONB,
  metadata_val JSONB DEFAULT '{}'
) RETURNS UUID AS $$
DECLARE
  event_id UUID;
BEGIN
  INSERT INTO public.analytics_events (
    company_id,
    user_id,
    event_type,
    event_data,
    metadata
  ) VALUES (
    company_uuid,
    user_uuid,
    event_type_val,
    event_data_val,
    metadata_val
  ) RETURNING id INTO event_id;
  
  RETURN event_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get company analytics summary
CREATE OR REPLACE FUNCTION get_company_analytics(
  company_uuid UUID,
  period_days INTEGER DEFAULT 30
) RETURNS JSONB AS $$
DECLARE
  result JSONB;
  total_orders INTEGER;
  total_shipments INTEGER;
  avg_order_value DECIMAL;
  top_suppliers JSONB;
BEGIN
  -- Get basic metrics
  SELECT 
    COUNT(*),
    COALESCE(AVG(total_amount), 0)
  INTO total_orders, avg_order_value
  FROM public.orders
  WHERE company_id = company_uuid
    AND created_at >= NOW() - INTERVAL '1 day' * period_days;
    
  SELECT COUNT(*) INTO total_shipments
  FROM public.shipments
  WHERE company_id = company_uuid
    AND created_at >= NOW() - INTERVAL '1 day' * period_days;
  
  -- Get top suppliers by order volume
  SELECT jsonb_agg(supplier_data) INTO top_suppliers
  FROM (
    SELECT jsonb_build_object(
      'id', s.id,
      'name', s.name,
      'order_count', COUNT(o.id),
      'total_value', COALESCE(SUM(o.total_amount), 0)
    ) as supplier_data
    FROM public.suppliers s
    LEFT JOIN public.orders o ON s.id = o.supplier_id 
      AND o.created_at >= NOW() - INTERVAL '1 day' * period_days
    WHERE s.company_id = company_uuid
    GROUP BY s.id, s.name
    ORDER BY COUNT(o.id) DESC
    LIMIT 5
  ) top_5;
  
  -- Build result
  result := jsonb_build_object(
    'period_days', period_days,
    'total_orders', total_orders,
    'total_shipments', total_shipments,
    'avg_order_value', avg_order_value,
    'top_suppliers', COALESCE(top_suppliers, '[]'::jsonb),
    'generated_at', NOW()
  );
  
  RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic status updates
CREATE TRIGGER inventory_status_trigger
  BEFORE UPDATE ON public.inventory
  FOR EACH ROW
  EXECUTE FUNCTION update_inventory_status();

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION calculate_inventory_risk(INTEGER, INTEGER, INTEGER, DECIMAL) TO authenticated;
GRANT EXECUTE ON FUNCTION calculate_supplier_score(UUID, INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION search_knowledge_base(vector(1536), UUID, DECIMAL, INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION create_inventory_risk_assessment(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION log_analytics_event(UUID, UUID, TEXT, JSONB, JSONB) TO authenticated;
GRANT EXECUTE ON FUNCTION get_company_analytics(UUID, INTEGER) TO authenticated;
