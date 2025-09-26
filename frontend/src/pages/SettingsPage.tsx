import React, { useState } from 'react';

const SettingsPage: React.FC = () => {
  const [apiUrl, setApiUrl] = useState('/api');
  const [apiKey, setApiKey] = useState('');
  const [orgName, setOrgName] = useState('SupplyMind');
  const [notifications, setNotifications] = useState(true);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    // Save settings via backend API
    await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ apiUrl, apiKey, orgName, notifications })
    });
    alert('Settings saved');
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Settings</h1>

      <form onSubmit={handleSave} className="bg-white rounded-lg border p-6 space-y-4 max-w-2xl">
        <div>
          <label className="block text-sm font-medium text-gray-700">Backend API URL</label>
          <input
            value={apiUrl}
            onChange={(e)=>setApiUrl(e.target.value)}
            className="mt-1 w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">API Key (optional)</label>
          <input
            type="password"
            value={apiKey}
            onChange={(e)=>setApiKey(e.target.value)}
            className="mt-1 w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Organization Name</label>
          <input
            value={orgName}
            onChange={(e)=>setOrgName(e.target.value)}
            className="mt-1 w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center gap-2">
          <input id="notifications" type="checkbox" checked={notifications} onChange={(e)=>setNotifications(e.target.checked)} />
          <label htmlFor="notifications" className="text-sm text-gray-700">Enable notifications</label>
        </div>

        <div className="pt-4">
          <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Save Settings</button>
        </div>
      </form>
    </div>
  );
};

export default SettingsPage;
