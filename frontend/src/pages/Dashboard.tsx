import React from 'react';
import { TrendingUp, Package, ShoppingCart, DollarSign } from 'lucide-react';
import CopilotChat from '../components/CopilotChat';

// Simple reusable chart widgets using SVG for no external deps
const Sparkline: React.FC<{ points: number[]; color?: string }> = ({ points, color = '#2563eb' }) => {
  const width = 120;
  const height = 40;
  const max = Math.max(...points, 1);
  const path = points.map((p, i) => {
    const x = (i / (points.length - 1)) * width;
    const y = height - (p / max) * height;
    return `${i === 0 ? 'M' : 'L'}${x},${y}`;
  }).join(' ');
  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      <path d={path} fill="none" stroke={color} strokeWidth="2" />
    </svg>
  );
};

const StatCard: React.FC<{ title: string; value: string; change: string; icon: React.ReactNode; trend?: number[] }>=({ title, value, change, icon, trend })=> (
  <div className="bg-white rounded-lg border p-4 flex items-center justify-between gap-4">
    <div>
      <div className="text-sm text-gray-500">{title}</div>
      <div className="text-2xl font-semibold text-gray-900">{value}</div>
      <div className={`text-sm ${change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>{change}</div>
    </div>
    <div className="flex items-center gap-4">
      <div className="p-2 rounded-full bg-blue-50 text-blue-600">{icon}</div>
      {trend && <Sparkline points={trend} />}
    </div>
  </div>
);

const Dashboard: React.FC = () => {
  // Placeholder stats and trends; integrate with API later
  const stats = [
    { title: 'Revenue', value: '$125,430', change: '+5.2%', icon: <DollarSign className="w-6 h-6" />, trend: [5,6,4,7,8,9,6,8] },
    { title: 'Orders', value: '1,240', change: '+2.1%', icon: <ShoppingCart className="w-6 h-6" />, trend: [12,10,14,13,15,16,18,20] },
    { title: 'Units in Stock', value: '18,930', change: '-0.8%', icon: <Package className="w-6 h-6" />, trend: [20,19,19,18,18,19,18,17] },
    { title: 'Growth', value: '3.1%', change: '+0.4%', icon: <TrendingUp className="w-6 h-6" />, trend: [1,2,1,3,2,3,4,3] },
  ];

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((s) => (
          <StatCard key={s.title} {...s} />
        ))}
      </div>

      {/* Charts (placeholder widgets) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg border p-4 lg:col-span-2">
          <h2 className="font-semibold text-gray-900 mb-2">Sales Trend</h2>
          <Sparkline points={[10,12,9,14,16,18,17,20,24,22,26,30]} color="#10b981" />
        </div>
        <div className="bg-white rounded-lg border p-4">
          <h2 className="font-semibold text-gray-900 mb-2">Inventory Turnover</h2>
          <Sparkline points={[3,4,3,5,4,6,5,7,6,8]} color="#f59e0b" />
        </div>
      </div>

      {/* Copilot Chat Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg border p-4">
            <h2 className="font-semibold text-gray-900 mb-2">Ask Copilot</h2>
            <p className="text-sm text-gray-500 mb-3">Ask about performance, risks, and recommendations.</p>
            <CopilotChat />
          </div>
        </div>
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg border p-4">
            <h2 className="font-semibold text-gray-900 mb-2">Context</h2>
            <p className="text-sm text-gray-600">The dashboard aggregates sales, inventory, and order signals. Connect the API to replace placeholder data.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
