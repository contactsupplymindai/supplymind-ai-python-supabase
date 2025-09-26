import React, { useEffect, useState } from 'react';
import { EyeIcon, ShoppingCartIcon } from '@heroicons/react/24/outline';

interface Order {
  id: string;
  order_number: string;
  customer_name: string;
  created_at: string;
  item_count: number;
  total_amount: number;
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
}

interface OrdersTableProps {
  orders: Order[];
  onOrderSelect?: (order: Order) => void;
}

type SortField = keyof Order;
type SortDirection = 'asc' | 'desc';

const OrdersTable: React.FC<OrdersTableProps> = ({ orders, onOrderSelect }) => {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  const getStatusPill = (status: Order['status']) => {
    const statusColors = {
      pending: 'bg-yellow-100 text-yellow-800',
      processing: 'bg-blue-100 text-blue-800',
      shipped: 'bg-purple-100 text-purple-800',
      delivered: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
    };

    return (
      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusColors[status]}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const SortHeader: React.FC<{ field: SortField; children: React.ReactNode }> = ({ field, children }) => {
    const isActive = sortField === field;
    return (
      <th 
        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
        onClick={() => {
          if (isActive) {
            setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
          } else {
            setSortField(field);
            setSortDirection('asc');
          }
        }}
      >
        <div className="flex items-center space-x-1">
          <span>{children}</span>
          {isActive && (
            <span className="text-blue-500">
              {sortDirection === 'asc' ? '↑' : '↓'}
            </span>
          )}
        </div>
      </th>
    );
  };

  // FIXED: Improved sorting logic with proper null/undefined checks
  const filtered = orders
    .filter(o =>
      [o.order_number, o.customer_name, o.status]
        .join(' ').toLowerCase().includes(search.toLowerCase()) &&
      (statusFilter === 'all' || o.status === statusFilter)
    )
    .sort((a, b) => {
      let av = a[sortField];
      let bv = b[sortField];
      
      // Handle undefined/null values
      if (av === undefined || av === null) av = '';
      if (bv === undefined || bv === null) bv = '';
      
      // Handle date fields
      if (typeof av === 'string' && sortField === 'created_at') {
        av = new Date(av).getTime();
        bv = new Date(String(bv)).getTime();
      }
      
      // Handle string comparisons
      if (typeof av === 'string' && typeof bv === 'string') {
        av = av.toLowerCase();
        bv = bv.toLowerCase();
      }
      
      // Safe comparison with proper type checking
      if (av < bv) return sortDirection === 'asc' ? -1 : 1;
      if (av > bv) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

  return (
    <div className="space-y-4">
      {/* Search and Filter Controls */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <input
            type="text"
            placeholder="Search orders..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="all">All Status</option>
          <option value="pending">Pending</option>
          <option value="processing">Processing</option>
          <option value="shipped">Shipped</option>
          <option value="delivered">Delivered</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>

      {/* Results Count */}
      <div className="text-sm text-gray-700">
        Showing {filtered.length} of {orders.length} orders
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
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filtered.map(order => (
              <tr key={order.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {order.order_number}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {order.customer_name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {new Date(order.created_at).toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {order.item_count}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${order.total_amount.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getStatusPill(order.status)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => onOrderSelect?.(order)}
                    className="text-blue-600 hover:text-blue-900 flex items-center gap-1"
                  >
                    <EyeIcon className="w-4 h-4" />
                    View
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-12">
          <ShoppingCartIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No orders found</h3>
          <p className="mt-1 text-sm text-gray-500">Try adjusting your search or filters.</p>
        </div>
      )}
    </div>
  );
};

export default OrdersTable;
