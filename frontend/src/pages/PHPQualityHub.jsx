import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import axios from 'axios';
import { Code, Shield, CheckCircle, Bug, Loader2, Wand2 } from 'lucide-react';
import { API } from '../App';

const PHPQualityHub = () => {
  const [projectPath, setProjectPath] = useState('');
  const [selectedTool, setSelectedTool] = useState('phpstan');
  const [activeTab, setActiveTab] = useState('analyze');

  // Fetch capabilities
  const { data: capabilities, isLoading } = useQuery({
    queryKey: ['php-quality-capabilities'],
    queryFn: async () => {
      const res = await axios.get(`${API}/hybrid/php-quality/capabilities`);
      return res.data;
    }
  });

  // Analyze code mutation
  const analyzeCode = useMutation({
    mutationFn: async ({ path, tool }) => {
      const token = localStorage.getItem('nexus_token');
      const res = await axios.post(
        `${API}/hybrid/php-quality/analyze?project_path=${encodeURIComponent(path)}&tool=${tool}`,
        {},
        { headers: { Authorization: `Bearer ${token}` }}
      );
      return res.data;
    }
  });

  // Fix code style mutation
  const fixCodeStyle = useMutation({
    mutationFn: async (path) => {
      const token = localStorage.getItem('nexus_token');
      const res = await axios.post(
        `${API}/hybrid/php-quality/fix-style?project_path=${encodeURIComponent(path)}`,
        {},
        { headers: { Authorization: `Bearer ${token}` }}
      );
      return res.data;
    }
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-400 to-purple-500 bg-clip-text text-transparent mb-2">
            🐘 PHP Code Quality
          </h1>
          <p className="text-gray-400">Static analysis, style fixing & security scanning</p>
          {capabilities && (
            <p className="text-sm text-indigo-400 mt-2">
              {capabilities.tools_count} tools • {capabilities.total_stars?.toLocaleString()} stars
            </p>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b border-gray-800">
          {['analyze', 'fix-style', 'tools'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 capitalize transition-colors ${
                activeTab === tab
                  ? 'text-indigo-400 border-b-2 border-indigo-400'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              {tab.replace('-', ' ')}
            </button>
          ))}
        </div>

        {/* Analyze Tab */}
        {activeTab === 'analyze' && (
          <div className="bg-gray-900/50 backdrop-blur border border-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-6">
              <Bug className="w-6 h-6 text-red-400" />
              <h2 className="text-2xl font-semibold">Analyze PHP Code</h2>
            </div>
            
            <div className="space-y-4">
              <select
                value={selectedTool}
                onChange={(e) => setSelectedTool(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white"
              >
                <option value="phpstan">PHPStan</option>
                <option value="psalm">Psalm</option>
                <option value="phan">Phan</option>
                <option value="phpmd">PHPMD</option>
              </select>

              <input
                type="text"
                placeholder="Project path or repository URL"
                value={projectPath}
                onChange={(e) => setProjectPath(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white"
              />
              
              <button
                onClick={() => analyzeCode.mutate({ path: projectPath, tool: selectedTool })}
                disabled={!projectPath || analyzeCode.isPending}
                className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-700 px-6 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2"
              >
                {analyzeCode.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Shield className="w-4 h-4" />
                )}
                Run Analysis
              </button>

              {analyzeCode.isSuccess && analyzeCode.data && (
                <div className="bg-indigo-900/30 border border-indigo-700 rounded-lg p-6">
                  <h3 className="text-xl font-semibold mb-3">Analysis Results</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-gray-800 rounded-lg p-4">
                      <p className="text-2xl font-bold text-red-400">{analyzeCode.data.errors_found}</p>
                      <p className="text-xs text-gray-400">Errors</p>
                    </div>
                    <div className="bg-gray-800 rounded-lg p-4">
                      <p className="text-2xl font-bold text-yellow-400">{analyzeCode.data.warnings_found}</p>
                      <p className="text-xs text-gray-400">Warnings</p>
                    </div>
                    <div className="bg-gray-800 rounded-lg p-4">
                      <p className="text-2xl font-bold text-blue-400">{analyzeCode.data.files_analyzed}</p>
                      <p className="text-xs text-gray-400">Files</p>
                    </div>
                    <div className="bg-gray-800 rounded-lg p-4">
                      <p className="text-2xl font-bold text-green-400">{analyzeCode.data.quality_score}</p>
                      <p className="text-xs text-gray-400">Score</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Fix Style Tab */}
        {activeTab === 'fix-style' && (
          <div className="bg-gray-900/50 backdrop-blur border border-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-6">
              <Wand2 className="w-6 h-6 text-purple-400" />
              <h2 className="text-2xl font-semibold">Auto-Fix Code Style</h2>
            </div>
            
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Project path"
                value={projectPath}
                onChange={(e) => setProjectPath(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white"
              />
              
              <button
                onClick={() => fixCodeStyle.mutate(projectPath)}
                disabled={!projectPath || fixCodeStyle.isPending}
                className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 px-6 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2"
              >
                {fixCodeStyle.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Wand2 className="w-4 h-4" />
                )}
                Fix Code Style
              </button>

              {fixCodeStyle.isSuccess && fixCodeStyle.data && (
                <div className="bg-purple-900/30 border border-purple-700 rounded-lg p-6">
                  <CheckCircle className="w-6 h-6 text-green-400 mb-3" />
                  <p className="text-green-400 font-semibold mb-2">Code Style Fixed!</p>
                  <p className="text-gray-400 text-sm">Files Fixed: {fixCodeStyle.data.files_fixed}</p>
                  <p className="text-gray-400 text-sm">Issues Fixed: {fixCodeStyle.data.issues_fixed}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tools Tab */}
        {activeTab === 'tools' && capabilities && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {capabilities.categories?.map((category, idx) => (
              <div key={idx} className="bg-gray-900/50 backdrop-blur border border-gray-800 rounded-lg p-6">
                <Code className="w-8 h-8 text-indigo-400 mb-3" />
                <h3 className="text-xl font-semibold mb-2 capitalize">{category.replace('-', ' ')}</h3>
                <p className="text-gray-400 text-sm">PHP code quality tools</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PHPQualityHub;
