import React from 'react';
import InventoryTable from '../components/InventoryTable';

const Inventory: React.FC = () => {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Inventory</h1>
      <InventoryTable />
    </div>
  );
};

export default Inventory;
