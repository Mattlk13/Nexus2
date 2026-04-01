import React, { useState, useEffect } from 'react';
import { Cloud, Server, Database, Zap, Lock, Image, Video, Network, GitBranch, Cpu, HardDrive, Shield } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

function CloudflareAdmin() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [capabilities, setCapabilities] = useState(null);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [workers, setWorkers] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCapabilities();
    fetchDashboard();
  }, []);

  const fetchCapabilities = async () => {
    try {
      const res = await fetch(`${API}/api/v2/hybrid/cloudflare_admin/capabilities`);
      const data = await res.json();
      setCapabilities(data);
    } catch (err) {
      console.error('Failed to fetch capabilities:', err);
    }
  };

  const fetchDashboard = async () => {
    try {
      const res = await fetch(`${API}/api/v2/hybrid/cloudflare_admin/dashboard`);
      const data = await res.json();
      setDashboardStats(data.stats);
    } catch (err) {
      console.error('Failed to fetch dashboard:', err);
    }
  };

  const fetchWorkers = async () => {
    try {
      const res = await fetch(`${API}/api/v2/hybrid/cloudflare_admin/workers`);
      const data = await res.json();
      setWorkers(data.workers || []);
    } catch (err) {
      console.error('Failed to fetch workers:', err);
    }
  };

  useEffect(() => {
    if (activeTab === 'workers') {
      fetchWorkers();
    }
  }, [activeTab]);

  const products = [
    { id: 'workers', icon: Server, name: 'Workers', color: 'orange' },
    { id: 'kv', icon: Database, name: 'KV Storage', color: 'blue' },
    { id: 'r2', icon: HardDrive, name: 'R2 Storage', color: 'purple' },
    { id: 'pages', icon: GitBranch, name: 'Pages', color: 'green' },
    { id: 'd1', icon: Database, name: 'D1 Database', color: 'cyan' },
    { id: 'ai_gateway', icon: Cpu, name: 'AI Gateway', color: 'pink' },
    { id: 'vectorize', icon: Network, name: 'Vectorize', color: 'indigo' },
    { id: 'workers_ai', icon: Zap, name: 'Workers AI', color: 'yellow' },
    { id: 'zero_trust', icon: Shield, name: 'Zero Trust', color: 'red' },
    { id: 'stream', icon: Video, name: 'Stream', color: 'teal' },
    { id: 'images', icon: Image, name: 'Images', color: 'emerald' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-blue-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <Cloud className="w-10 h-10 text-orange-600" />
                <h1 className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-blue-600 bg-clip-text text-transparent">
                  Cloudflare Admin
                </h1>
              </div>
              <p className="text-gray-600">Complete developer platform management</p>
            </div>
            {capabilities && (
              <div className="text-right">
                <div className="text-3xl font-bold text-orange-600">{Object.keys(capabilities.products).length}</div>
                <div className="text-sm text-gray-600">Products</div>
              </div>
            )}
          </div>

          {/* Global Stats */}
          {dashboardStats && (
            <div className="grid grid-cols-5 gap-4 mt-6">
              <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4">
                <div className="text-2xl font-bold text-orange-900">{dashboardStats.workers_deployed}</div>
                <div className="text-sm text-gray-600">Workers</div>
              </div>
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
                <div className="text-2xl font-bold text-blue-900">{dashboardStats.kv_namespaces}</div>
                <div className="text-sm text-gray-600">KV Namespaces</div>
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
                <div className="text-2xl font-bold text-purple-900">{dashboardStats.r2_buckets}</div>
                <div className="text-sm text-gray-600">R2 Buckets</div>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
                <div className="text-2xl font-bold text-green-900">{dashboardStats.pages_projects}</div>
                <div className="text-sm text-gray-600">Pages Projects</div>
              </div>
              <div className="bg-gradient-to-br from-cyan-50 to-cyan-100 rounded-lg p-4">
                <div className="text-2xl font-bold text-cyan-900">{dashboardStats.d1_databases}</div>
                <div className="text-sm text-gray-600">D1 Databases</div>
              </div>
            </div>
          )}
        </div>

        {/* Products Grid */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">☁️ Cloudflare Products</h2>
          <div className="grid grid-cols-4 gap-4">
            {products.map((product) => (
              <button
                key={product.id}
                onClick={() => setActiveTab(product.id)}
                className={`p-6 rounded-xl border-2 transition-all hover:shadow-lg ${
                  activeTab === product.id
                    ? `border-${product.color}-500 bg-${product.color}-50`
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <product.icon className={`w-8 h-8 text-${product.color}-600 mb-3`} />
                <div className="font-semibold text-gray-900">{product.name}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Content Area */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Dashboard Tab */}
          {activeTab === 'dashboard' && capabilities && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Platform Overview</h2>
              
              <div className="grid grid-cols-2 gap-6">
                {Object.entries(capabilities.products).map(([key, product]) => (
                  <div key={key} className="border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow">
                    <h3 className="font-bold text-lg text-gray-900 mb-2">{product.name}</h3>
                    <p className="text-gray-600 text-sm mb-4">{product.description}</p>
                    <div className="space-y-1">
                      {product.capabilities.map((cap, idx) => (
                        <div key={idx} className="text-xs text-gray-500">• {cap}</div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {capabilities.global_network && (
                <div className="mt-8 bg-gradient-to-r from-orange-50 to-blue-50 rounded-xl p-6">
                  <h3 className="font-bold text-lg mb-4">🌍 Global Network</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <div className="text-2xl font-bold text-orange-600">
                        {capabilities.global_network.edge_locations}
                      </div>
                      <div className="text-sm text-gray-600">Edge Locations</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-blue-600">
                        {capabilities.global_network.coverage}
                      </div>
                      <div className="text-sm text-gray-600">Global Coverage</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-purple-600">
                        {capabilities.global_network.latency}
                      </div>
                      <div className="text-sm text-gray-600">Avg Latency</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Workers Tab */}
          {activeTab === 'workers' && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">⚡ Cloudflare Workers</h2>
              
              <div className="bg-orange-50 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-orange-900 mb-2">Serverless Compute at the Edge</h3>
                <p className="text-sm text-gray-600">Deploy code globally with zero cold starts and automatic scaling</p>
              </div>

              <div className="space-y-4">
                {workers.length > 0 ? (
                  workers.map((worker, idx) => (
                    <div key={idx} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="font-semibold text-lg">{worker.name}</div>
                          <div className="text-sm text-gray-600">{worker.route}</div>
                        </div>
                        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                          {worker.status}
                        </span>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <Server className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                    <p>No workers deployed yet</p>
                    <button className="mt-4 px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700">
                      Deploy Your First Worker
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Other product tabs would follow similar patterns */}
          {activeTab !== 'dashboard' && activeTab !== 'workers' && (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">☁️</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                {products.find(p => p.id === activeTab)?.name}
              </h3>
              <p className="text-gray-600">Management interface coming soon</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default CloudflareAdmin;
