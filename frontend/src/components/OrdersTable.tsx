import React, { useEffect, useState } from 'react';
import { ShoppingCart, Search, ChevronDown, ChevronUp, AlertTriangle, CheckCircle, Clock, Eye } from 'lucide-react';

export interface Order {
  id: string;
  order_number: string;
  customer_name: string;
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  total_amount: number;
  item_count: number;
  created_at: string; // ISO string
  expected_ship_date?: string; // ISO string
}

interface OrdersTableProps {
  className?: string;
  onOrderSelect?: (order: Order) => void;
}

export const OrdersTable: React.FC<OrdersTableProps> = ({ className, onOrderSelect }) => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [sortField, setSortField] = useState<keyof Order>('created_at');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [statusFilter, setStatusFilter] = useState<'all' | Order['status']>('all');

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/orders');
      if (!res.ok) throw new Error('Failed to fetch orders');
      const data = await res.json();
      setOrders(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load orders');
      console.error('Orders fetch error:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field: keyof Order) => {
    if (sortField === field) setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    else { setSortField(field); setSortDirection('asc'); }
  };

  const getStatusPill = (status: Order['status']) => {
    const map = {
      pending: 'bg-yellow-100 text-yellow-700',
      processing: 'bg-blue-100 text-blue-700',
      shipped: 'bg-indigo-100 text-indigo-700',
      delivered: 'bg-green-100 text-green-700',
      cancelled: 'bg-red-100 text-red-700',
    } as const;
    const iconMap = {
      pending: <Clock className="w-4 h-4" />,
      processing: <Clock className="w-4 h-4" />,
      shipped: <Clock className="w-4 h-4" />,
      delivered: <CheckCircle className="w-4 h-4" />,
      cancelled: <AlertTriangle className="w-4 h-4" />,
    } as const;
    return (
      <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${map[status]}`}>
        {iconMap[status]}
        {status.toUpperCase()}
      </span>
    );
  };

  const filtered = orders
    .filter(o =>
      [o.order_number, o.customer_name, o.status]
        .join(' ').toLowerCase().includes(search.toLowerCase()) &&
      (statusFilter === 'all' || o.status === statusFilter)
    )
    .sort((a, b) => {
      let av = a[sortField];
      let bv = b[sortField];
      if (typeof av === 'string' && sortField !== 'customer_name') {
        // date or id compare
        av = new Date(av).getTime();
        bv = new Date(String(bv)).getTime();
      }
      if (typeof av === 'string') av = av.toLowerCase();
      if (typeof bv === 'string') bv = (bv as string).toLowerCase();
      if (av < bv) return sortDirection === 'asc' ? -1 : 1;
      if (av > bv) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

  const SortHeader: React.FC<{ field: keyof Order; children: React.ReactNode }>=({ field, children })=> (
    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-50"
        onClick={() => handleSort(field)}>
      <div className="flex items-center gap-1">
        {children}
        {sortField === field && (sortDirection === 'asc' ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />)}
      </div>
    </th>
  );

  if (loading) {
    return (
      <div className={`bg-white rounded-lg border ${className || ''}`}>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2">Loading orders...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg border ${className || ''}`}>
        <div className="flex items-center justify-center h-64 text-red-600">
          <AlertTriangle className="w-6 h-6 mr-2" />
          <span>Error loading orders: {error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg border ${className || ''}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShoppingCart className="h-6 w-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">Orders</h2>
          </div>
          <div className="text-sm text-gray-500">Total: {filtered.length}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="px-6 py-4 bg-gray-50 border-b border-gray-200 flex flex-wrap gap-4 items-center">
        <div className="relative flex-1 min-w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            value={search}
            onChange={(e)=>setSearch(e.target.value)}
            placeholder="Search orders by #, customer, or status..."
            className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div>
          <select
            value={statusFilter}
            onChange={(e)=>setStatusFilter(e.target.value as typeof statusFilter)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="shipped">Shipped</option>
            <option value="delivered">Delivered</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <SortHeader field="order_number">Order #</SortHeader>
              <SortHeader field="customer_name">Customer</SortHeader>
              <SortHeader field="created_at">Created</SortHeader>
              <SortHeader field="item_count">Items</SortHeader>
              <SortHeader field="total_amount">Total</SortHeader>
              <SortHeader field="status">Status</SortHeader>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filtered.map(order => (
              <tr key={order.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{order.order_number}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{order.customer_name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{new Date(order.created_at).toLocaleString()}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{order.item_count}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${order.total_amount.toFixed(2)}</td>
                <td className="px-6 py-4 whitespace-nowrap">{getStatusPill(order.status)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button onClick={()=>onOrderSelect?.(order)} className="text-blue-600 hover:text-blue-900 flex items-center gap-1">
                    <Eye className="w-4 h-4" /> View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-12">
          <ShoppingCart className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No orders found</h3>
          <p className="mt-1 text-sm text-gray-500">Try adjusting your search or filters.</p>
        </div>
      )}
    </div>
  );
};

export default OrdersTable;
