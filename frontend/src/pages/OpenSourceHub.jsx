import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import axios from 'axios';
import { Package, Star, GitBranch, Bell, Rocket, Loader2, CheckCircle } from 'lucide-react';
import { API } from '../App';

const OpenSourceHub = () => {
  const [activeTab, setActiveTab] = useState('tools');
  const [repoUrl, setRepoUrl] = useState('');

  // Fetch open source tools
  const { data: toolsData, isLoading } = useQuery({
    queryKey: ['opensource-tools'],
    queryFn: async () => {
      const res = await axios.get(`${API}/hybrid/opensource-tools/list?category=all`);
      return res.data;
    }
  });

  // Automate release mutation
  const automateRelease = useMutation({
    mutationFn: async (repo) => {
      const token = localStorage.getItem('nexus_token');
      const res = await axios.post(
        `${API}/hybrid/opensource-tools/automate-release?repo=${repo}`,
        {},
        { headers: { Authorization: `Bearer ${token}` }}
      );
      return res.data;
    }
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-green-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent mb-2">
            🔧 Open Source Tools Hub
          </h1>
          <p className="text-gray-400">Software to make running your open source project easier</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b border-gray-800">
          {['tools', 'automation', 'probot'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 capitalize transition-colors ${
                activeTab === tab
                  ? 'text-green-400 border-b-2 border-green-400'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Tools Tab */}
        {activeTab === 'tools' && toolsData && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {toolsData.tools?.map((tool, idx) => (
              <div key={idx} className="bg-gray-900/50 backdrop-blur border border-gray-800 rounded-lg p-6 hover:border-green-400/50 transition-all">
                <div className="flex items-start justify-between mb-3">
                  <Package className="w-8 h-8 text-green-400" />
                  <Star className="w-5 h-5 text-yellow-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{tool.name}</h3>
                <p className="text-gray-400 text-sm mb-3">{tool.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500">{tool.language}</span>
                  <span className="text-yellow-400 font-semibold text-sm">⭐ {tool.stars.toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Automation Tab */}
        {activeTab === 'automation' && (
          <div className="bg-gray-900/50 backdrop-blur border border-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-6">
              <Rocket className="w-6 h-6 text-green-400" />
              <h2 className="text-2xl font-semibold">Automate Release Process</h2>
            </div>
            
            <div className="space-y-4">
              <p className="text-gray-400">Use semantic-release to automate version management and package publishing</p>
              
              <input
                type="text"
                placeholder="Repository URL (e.g., username/repo)"
                value={repoUrl}
                onChange={(e) => setRepoUrl(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white"
              />
              
              <button
                onClick={() => automateRelease.mutate(repoUrl)}
                disabled={!repoUrl || automateRelease.isPending}
                className="bg-green-600 hover:bg-green-700 disabled:bg-gray-700 px-6 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2"
              >
                {automateRelease.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <GitBranch className="w-4 h-4" />
                )}
                Setup Automated Release
              </button>

              {automateRelease.isSuccess && (
                <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
                  <CheckCircle className="w-5 h-5 text-green-400 mb-2" />
                  <p className="text-green-400 font-semibold">Release Automation Configured!</p>
                  <p className="text-gray-400 text-sm mt-1">Version: {automateRelease.data?.version_released}</p>
                  <p className="text-gray-400 text-sm">Changelog: {automateRelease.data?.changelog_generated ? '✅ Generated' : '❌'}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Probot Tab */}
        {activeTab === 'probot' && (
          <div className="space-y-4">
            <div className="bg-gradient-to-r from-green-900/30 to-blue-900/30 border border-green-700/50 rounded-lg p-6">
              <Bell className="w-8 h-8 text-green-400 mb-3" />
              <h3 className="text-xl font-semibold mb-2">GitHub Probot Apps</h3>
              <p className="text-gray-400">13 automation apps available - WIP, Stale, DCO, TODO, Welcome & more</p>
              <a href="/probot-apps" className="inline-block mt-4 text-green-400 hover:text-green-300 font-semibold">
                View All Apps →
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OpenSourceHub;
