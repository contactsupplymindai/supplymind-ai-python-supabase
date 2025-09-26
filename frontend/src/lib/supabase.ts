import { createClient } from '@supabase/supabase-js';

// Supabase Configuration
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'your-supabase-url';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'your-supabase-anon-key';

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error(
    'Missing Supabase environment variables. Please check NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY'
  );
}

// Create Supabase client
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
  },
  realtime: {
    params: {
      eventsPerSecond: 10,
    },
  },
});

// Database Tables TypeScript interfaces
export interface User {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
  first_name?: string;
  last_name?: string;
  avatar_url?: string;
  role: 'admin' | 'user' | 'manager';
}

export interface InventoryItem {
  id: string;
  name: string;
  description?: string;
  sku: string;
  category: string;
  quantity: number;
  min_stock_level: number;
  max_stock_level: number;
  unit_price: number;
  supplier_id?: string;
  location?: string;
  created_at: string;
  updated_at: string;
  status: 'active' | 'discontinued' | 'out_of_stock';
}

export interface Order {
  id: string;
  order_number: string;
  customer_name: string;
  customer_email: string;
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  total_amount: number;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
  shipping_address?: string;
  notes?: string;
}

export interface OrderItem {
  id: string;
  order_id: string;
  inventory_item_id: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface Supplier {
  id: string;
  name: string;
  contact_person?: string;
  email?: string;
  phone?: string;
  address?: string;
  created_at: string;
  updated_at: string;
  status: 'active' | 'inactive';
}

export interface ChatSession {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
  status: 'active' | 'archived';
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  metadata?: Record<string, any>;
}

export interface AnalyticsMetric {
  id: string;
  metric_name: string;
  metric_value: number;
  metric_type: 'revenue' | 'inventory' | 'orders' | 'customers';
  period: 'daily' | 'weekly' | 'monthly' | 'yearly';
  date: string;
  created_at: string;
}

// Authentication helper functions
export const auth = {
  signUp: async (email: string, password: string, userData?: Partial<User>) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: userData,
      },
    });
    return { data, error };
  },

  signIn: async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    return { data, error };
  },

  signOut: async () => {
    const { error } = await supabase.auth.signOut();
    return { error };
  },

  getCurrentUser: async () => {
    const { data: { user }, error } = await supabase.auth.getUser();
    return { user, error };
  },

  resetPassword: async (email: string) => {
    const { data, error } = await supabase.auth.resetPasswordForEmail(email);
    return { data, error };
  },
};

// Database helper functions
export const db = {
  // Inventory operations
  inventory: {
    getAll: () => supabase.from('inventory_items').select('*').order('created_at', { ascending: false }),
    getById: (id: string) => supabase.from('inventory_items').select('*').eq('id', id).single(),
    create: (item: Omit<InventoryItem, 'id' | 'created_at' | 'updated_at'>) => 
      supabase.from('inventory_items').insert(item).select().single(),
    update: (id: string, updates: Partial<InventoryItem>) => 
      supabase.from('inventory_items').update(updates).eq('id', id).select().single(),
    delete: (id: string) => supabase.from('inventory_items').delete().eq('id', id),
    getLowStock: () => supabase.from('inventory_items')
      .select('*')
      .lt('quantity', supabase.from('inventory_items').select('min_stock_level'))
  },

  // Orders operations
  orders: {
    getAll: () => supabase.from('orders').select('*, items:order_items(*)').order('created_at', { ascending: false }),
    getById: (id: string) => supabase.from('orders').select('*, items:order_items(*)').eq('id', id).single(),
    create: (order: Omit<Order, 'id' | 'created_at' | 'updated_at'>) => 
      supabase.from('orders').insert(order).select().single(),
    update: (id: string, updates: Partial<Order>) => 
      supabase.from('orders').update(updates).eq('id', id).select().single(),
    delete: (id: string) => supabase.from('orders').delete().eq('id', id),
  },

  // Chat operations
  chat: {
    getSessions: (userId: string) => supabase.from('chat_sessions').select('*').eq('user_id', userId).order('updated_at', { ascending: false }),
    getMessages: (sessionId: string) => supabase.from('chat_messages').select('*').eq('session_id', sessionId).order('created_at', { ascending: true }),
    createSession: (session: Omit<ChatSession, 'id' | 'created_at' | 'updated_at'>) => 
      supabase.from('chat_sessions').insert(session).select().single(),
    addMessage: (message: Omit<ChatMessage, 'id' | 'created_at'>) => 
      supabase.from('chat_messages').insert(message).select().single(),
  },

  // Analytics operations
  analytics: {
    getMetrics: (type?: string, period?: string) => {
      let query = supabase.from('analytics_metrics').select('*');
      if (type) query = query.eq('metric_type', type);
      if (period) query = query.eq('period', period);
      return query.order('date', { ascending: false });
    },
    createMetric: (metric: Omit<AnalyticsMetric, 'id' | 'created_at'>) => 
      supabase.from('analytics_metrics').insert(metric).select().single(),
  },
};

// Real-time subscriptions
export const subscriptions = {
  inventory: (callback: (payload: any) => void) => {
    return supabase
      .channel('inventory_changes')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'inventory_items' }, callback)
      .subscribe();
  },

  orders: (callback: (payload: any) => void) => {
    return supabase
      .channel('order_changes')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'orders' }, callback)
      .subscribe();
  },

  chat: (sessionId: string, callback: (payload: any) => void) => {
    return supabase
      .channel(`chat_${sessionId}`)
      .on('postgres_changes', { 
        event: 'INSERT', 
        schema: 'public', 
        table: 'chat_messages',
        filter: `session_id=eq.${sessionId}`
      }, callback)
      .subscribe();
  },
};

export default supabase;
