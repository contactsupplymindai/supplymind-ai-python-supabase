import React from 'react';
import OrdersTable from '../components/OrdersTable';

const dummyOrders = []; // Replace with fetched data as needed

const Orders: React.FC = () => {
  return (
    <div>
      <h1>Orders</h1>
      <OrdersTable orders={dummyOrders} />
    </div>
  );
};

export default Orders;
