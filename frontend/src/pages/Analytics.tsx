import React from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const Analytics: React.FC = () => {
  // Sample data for analytics charts
  const salesData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Revenue ($)',
        data: [65000, 59000, 80000, 81000, 56000, 55000],
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
      },
      {
        label: 'Orders',
        data: [120, 100, 150, 180, 95, 110],
        backgroundColor: 'rgba(16, 185, 129, 0.5)',
        borderColor: 'rgba(16, 185, 129, 1)',
        borderWidth: 1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Revenue & Orders Trend',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  const inventoryMetrics = [
    { category: 'Electronics', turnover: 8.5, value: 245000 },
    { category: 'Clothing', turnover: 6.2, value: 180000 },
    { category: 'Books', turnover: 4.1, value: 95000 },
    { category: 'Home & Garden', turnover: 5.7, value: 320000 },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Analytics Dashboard
          </h1>
          <p className="text-gray-600">
            Monitor your supply chain performance and key metrics
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Revenue</h3>
            <p className="text-3xl font-bold text-green-600">$456,000</p>
            <p className="text-sm text-gray-500 mt-1">+12.5% from last month</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Total Orders</h3>
            <p className="text-3xl font-bold text-blue-600">1,248</p>
            <p className="text-sm text-gray-500 mt-1">+8.3% from last month</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Avg Order Value</h3>
            <p className="text-3xl font-bold text-purple-600">$365</p>
            <p className="text-sm text-gray-500 mt-1">+3.2% from last month</p>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Inventory Turnover</h3>
            <p className="text-3xl font-bold text-orange-600">6.2x</p>
            <p className="text-sm text-gray-500 mt-1">-0.5x from last month</p>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Revenue & Orders Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
              Revenue & Orders Trend
            </h3>
            <div style={{ height: '300px' }}>
              <Bar data={salesData} options={chartOptions} />
            </div>
          </div>

          {/* Inventory Categories */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">
              Inventory by Category
            </h3>
            <div className="space-y-4">
              {inventoryMetrics.map((item, index) => (
                <div key={index} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                  <div>
                    <h4 className="font-medium text-gray-800">{item.category}</h4>
                    <p className="text-sm text-gray-600">Turnover: {item.turnover}x/year</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-800">${item.value.toLocaleString()}</p>
                    <p className="text-sm text-gray-600">Total Value</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">
            Recent Supply Chain Events
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between py-3 border-b border-gray-200">
              <div>
                <p className="font-medium text-gray-800">Large order received from TechCorp</p>
                <p className="text-sm text-gray-600">Electronics category - $45,000 order value</p>
              </div>
              <span className="text-sm text-gray-500">2 hours ago</span>
            </div>
            
            <div className="flex items-center justify-between py-3 border-b border-gray-200">
              <div>
                <p className="font-medium text-gray-800">Low stock alert triggered</p>
                <p className="text-sm text-gray-600">iPhone 15 Pro - Only 12 units remaining</p>
              </div>
              <span className="text-sm text-gray-500">4 hours ago</span>
            </div>
            
            <div className="flex items-center justify-between py-3">
              <div>
                <p className="font-medium text-gray-800">Supplier delivery completed</p>
                <p className="text-sm text-gray-600">Samsung Electronics - 200 units received</p>
              </div>
              <span className="text-sm text-gray-500">6 hours ago</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
