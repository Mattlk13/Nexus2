import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { Brain, Search, Star, Database, Loader2, Sparkles } from 'lucide-react';
import { API } from '../App';

const AIModelsHub = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFramework, setSelectedFramework] = useState(null);

  // Fetch AI frameworks
  const { data: frameworksData, isLoading } = useQuery({
    queryKey: ['ai-frameworks'],
    queryFn: async () => {
      const res = await axios.get(`${API}/hybrid/ai-model-zoos/frameworks`);
      return res.data;
    }
  });

  // Fetch capabilities
  const { data: capabilities } = useQuery({
    queryKey: ['ai-model-zoos-capabilities'],
    queryFn: async () => {
      const res = await axios.get(`${API}/hybrid/ai-model-zoos/capabilities`);
      return res.data;
    }
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-cyan-500 bg-clip-text text-transparent mb-2">
            🧠 AI Model Zoos
          </h1>
          <p className="text-gray-400">Pre-trained models from TensorFlow, PyTorch, Caffe & more</p>
          {capabilities && (
            <p className="text-sm text-blue-400 mt-2">⭐ {capabilities.total_stars?.toLocaleString()} total stars</p>
          )}
        </div>

        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              placeholder="Search for pre-trained models..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-gray-900/50 border border-gray-800 rounded-lg pl-12 pr-4 py-4 text-white placeholder-gray-500"
            />
          </div>
        </div>

        {/* Frameworks Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {frameworksData?.frameworks?.map((framework, idx) => (
            <div
              key={idx}
              onClick={() => setSelectedFramework(framework)}
              className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 hover:border-blue-400/50 rounded-lg p-6 cursor-pointer transition-all transform hover:scale-105"
            >
              <div className="flex items-center justify-between mb-4">
                <Brain className="w-10 h-10 text-blue-400" />
                <Star className="w-5 h-5 text-yellow-400" />
              </div>
              <h3 className="text-2xl font-bold mb-2">{framework.name}</h3>
              <p className="text-gray-400 text-sm mb-3">{framework.language}</p>
              <div className="flex items-center justify-between">
                <span className="text-yellow-400 font-semibold">⭐ {framework.stars.toLocaleString()}</span>
                <span className="text-xs text-gray-500">{framework.repo}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Selected Framework Detail */}
        {selectedFramework && (
          <div className="mt-8 bg-blue-900/20 border border-blue-700/50 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-4">
              <Sparkles className="w-6 h-6 text-blue-400" />
              <h2 className="text-2xl font-semibold">{selectedFramework.name} Model Zoo</h2>
            </div>
            <p className="text-gray-400 mb-4">{selectedFramework.description || 'Browse pre-trained models'}</p>
            <div className="flex gap-4">
              <a
                href={`https://github.com/${selectedFramework.repo}`}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-semibold transition-colors"
              >
                View on GitHub
              </a>
              <button className="bg-gray-800 hover:bg-gray-700 px-6 py-3 rounded-lg font-semibold transition-colors">
                Browse Models
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIModelsHub;
