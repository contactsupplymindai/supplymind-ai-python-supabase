import React from 'react';
import OrdersTable from '../components/OrdersTable';

const Orders: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Orders</h1>
      <OrdersTable />
    </div>
  );
};

export default Orders;
