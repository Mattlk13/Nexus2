import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import axios from 'axios';
import { Code, Settings, AlertCircle, CheckCircle, Loader2, Hammer, GitBranch } from 'lucide-react';
import { API } from '../App';

const DevToolsHub = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [projectName, setProjectName] = useState('');

  // Fetch DevTools capabilities
  const { data: capabilities, isLoading: capLoading } = useQuery({
    queryKey: ['devtools-capabilities'],
    queryFn: async () => {
      const res = await axios.get(`${API}/hybrid/devtools/capabilities`);
      return res.data;
    }
  });

  // Fetch Editors capabilities
  const { data: editors, isLoading: editorsLoading } = useQuery({
    queryKey: ['editors'],
    queryFn: async () => {
      const res = await axios.get(`${API}/hybrid/editors/list`);
      return res.data;
    }
  });

  // Setup error tracking mutation
  const setupErrorTracking = useMutation({
    mutationFn: async (project) => {
      const token = localStorage.getItem('nexus_token');
      const res = await axios.post(
        `${API}/hybrid/devtools/error-tracking?project=${project}`,
        {},
        { headers: { Authorization: `Bearer ${token}` }}
      );
      return res.data;
    }
  });

  if (capLoading || editorsLoading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent mb-2">
            🛠️ Developer Tools Hub
          </h1>
          <p className="text-gray-400">Sentry, Jenkins, Gitpod, Editors & More</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b border-gray-800">
          {['overview', 'error-tracking', 'ci-pipeline', 'editors'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 capitalize transition-colors ${
                activeTab === tab
                  ? 'text-purple-400 border-b-2 border-purple-400'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              {tab.replace('-', ' ')}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && capabilities && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {capabilities.tools?.map((tool, idx) => (
              <div key={idx} className="bg-gray-900/50 backdrop-blur border border-gray-800 rounded-lg p-6">
                <Hammer className="w-8 h-8 text-purple-400 mb-3" />
                <h3 className="text-xl font-semibold mb-2">{tool}</h3>
                <p className="text-gray-400 text-sm">Development tool integration</p>
              </div>
            ))}
          </div>
        )}

        {/* Error Tracking Tab */}
        {activeTab === 'error-tracking' && (
          <div className="bg-gray-900/50 backdrop-blur border border-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-6">
              <AlertCircle className="w-6 h-6 text-red-400" />
              <h2 className="text-2xl font-semibold">Setup Sentry Error Tracking</h2>
            </div>
            
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Project name"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white"
              />
              
              <button
                onClick={() => setupErrorTracking.mutate(projectName)}
                disabled={!projectName || setupErrorTracking.isPending}
                className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 px-6 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2"
              >
                {setupErrorTracking.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Settings className="w-4 h-4" />
                )}
                Setup Error Tracking
              </button>

              {setupErrorTracking.isSuccess && (
                <div className="bg-green-900/30 border border-green-700 rounded-lg p-4 flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-400 mt-0.5" />
                  <div>
                    <p className="text-green-400 font-semibold">Sentry Setup Complete!</p>
                    <p className="text-gray-400 text-sm mt-1">DSN: {setupErrorTracking.data?.dsn}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* CI Pipeline Tab */}
        {activeTab === 'ci-pipeline' && (
          <div className="bg-gray-900/50 backdrop-blur border border-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-6">
              <GitBranch className="w-6 h-6 text-blue-400" />
              <h2 className="text-2xl font-semibold">Jenkins CI/CD Pipeline</h2>
            </div>
            
            <div className="space-y-4">
              <div className="flex gap-2">
                {['build', 'test', 'deploy'].map(stage => (
                  <div key={stage} className="flex-1 bg-gray-800 border border-gray-700 rounded-lg p-4 text-center">
                    <div className="text-sm text-gray-500 uppercase mb-1">Stage</div>
                    <div className="text-lg font-semibold capitalize">{stage}</div>
                  </div>
                ))}
              </div>
              <p className="text-gray-400 text-sm">Create automated CI/CD pipelines with Jenkins integration</p>
            </div>
          </div>
        )}

        {/* Editors Tab */}
        {activeTab === 'editors' && editors && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {Object.entries(editors.editors || {}).map(([name, info]) => (
              <div key={name} className="bg-gray-900/50 backdrop-blur border border-gray-800 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold capitalize">{name}</h3>
                  <Code className="w-5 h-5 text-purple-400" />
                </div>
                <p className="text-gray-400 text-sm mb-2">Language: {info.language}</p>
                <p className="text-purple-400 font-semibold">⭐ {info.stars.toLocaleString()} stars</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DevToolsHub;
