import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import axios from 'axios';
import { Boxes, Star, Code, Zap, Loader2, Download } from 'lucide-react';
import { API } from '../App';

const JSStateHub = () => {
  const [selectedLibs, setSelectedLibs] = useState([]);
  const [framework, setFramework] = useState('react');

  // Fetch state libraries
  const { data: librariesData, isLoading } = useQuery({
    queryKey: ['js-state-libraries'],
    queryFn: async () => {
      const res = await axios.get(`${API}/hybrid/js-state/libraries`);
      return res.data;
    }
  });

  // Compare libraries mutation
  const compareLibraries = useMutation({
    mutationFn: async (libNames) => {
      const res = await axios.post(
        `${API}/hybrid/js-state/compare`,
        { lib_names: libNames }
      );
      return res.data;
    }
  });

  const toggleLibSelection = (libName) => {
    setSelectedLibs(prev => 
      prev.includes(libName) 
        ? prev.filter(l => l !== libName)
        : [...prev, libName]
    );
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-cyan-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent mb-2">
            ⚛️ JavaScript State Management
          </h1>
          <p className="text-gray-400">Compare Redux, MobX, XState & more</p>
          {librariesData?.most_popular && (
            <p className="text-sm text-cyan-400 mt-2">Most Popular: {librariesData.most_popular}</p>
          )}
        </div>

        {/* Selection Controls */}
        <div className="mb-6 flex gap-4 items-center">
          <button
            onClick={() => compareLibraries.mutate(selectedLibs)}
            disabled={selectedLibs.length < 2 || compareLibraries.isPending}
            className="bg-cyan-600 hover:bg-cyan-700 disabled:bg-gray-700 px-6 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2"
          >
            {compareLibraries.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Zap className="w-4 h-4" />
            )}
            Compare Selected ({selectedLibs.length})
          </button>
          {selectedLibs.length > 0 && (
            <button
              onClick={() => setSelectedLibs([])}
              className="text-gray-400 hover:text-white transition-colors"
            >
              Clear Selection
            </button>
          )}
        </div>

        {/* Libraries Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {librariesData?.libraries?.map((lib, idx) => (
            <div
              key={idx}
              onClick={() => toggleLibSelection(lib.name)}
              className={`bg-gradient-to-br from-gray-900 to-gray-800 border rounded-lg p-6 cursor-pointer transition-all transform hover:scale-105 ${
                selectedLibs.includes(lib.name)
                  ? 'border-cyan-400 ring-2 ring-cyan-400/50'
                  : 'border-gray-700 hover:border-cyan-400/50'
              }`}
            >
              <div className="flex items-center justify-between mb-4">
                <Boxes className="w-10 h-10 text-cyan-400" />
                {selectedLibs.includes(lib.name) && (
                  <CheckCircle className="w-6 h-6 text-cyan-400" />
                )}
              </div>
              <h3 className="text-2xl font-bold mb-2">{lib.name}</h3>
              <p className="text-gray-400 text-sm mb-3">{lib.description}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">{lib.language}</span>
                <span className="text-yellow-400 font-semibold text-sm">⭐ {lib.stars.toLocaleString()}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Comparison Results */}
        {compareLibraries.isSuccess && compareLibraries.data && (
          <div className="mt-8 bg-cyan-900/20 border border-cyan-700/50 rounded-lg p-8">
            <h2 className="text-2xl font-semibold mb-4">Comparison Results</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              {compareLibraries.data.comparison?.map((lib, idx) => (
                <div key={idx} className="bg-gray-800 rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-2">{lib.name}</h3>
                  <p className="text-gray-400 text-sm mb-2">{lib.description}</p>
                  <p className="text-yellow-400 text-sm">⭐ {lib.stars.toLocaleString()}</p>
                </div>
              ))}
            </div>
            <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
              <p className="text-sm text-blue-400 font-semibold mb-1">💡 Recommendation:</p>
              <p className="text-gray-300">{compareLibraries.data.recommendation}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default JSStateHub;
