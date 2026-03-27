import React from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { Gamepad2, Play, Code, Loader2, ExternalLink } from 'lucide-react';
import { API } from '../App';

const WebGamesHub = () => {
  // Fetch games list
  const { data: gamesData, isLoading } = useQuery({
    queryKey: ['webgames'],
    queryFn: async () => {
      const res = await axios.get(`${API}/hybrid/webgames/list`);
      return res.data;
    }
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-pink-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-pink-400 to-purple-500 bg-clip-text text-transparent mb-2">
            🎮 Web Games Hub
          </h1>
          <p className="text-gray-400">Browser-based games - Play instantly, no downloads</p>
        </div>

        {/* Games Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {gamesData?.games?.map((game, idx) => (
            <div
              key={idx}
              className="bg-gradient-to-br from-purple-900/30 to-pink-900/30 border border-purple-700/50 rounded-lg p-6 hover:border-pink-400/50 transition-all"
            >
              <div className="flex items-center justify-between mb-4">
                <Gamepad2 className="w-10 h-10 text-pink-400" />
                <Play className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-2xl font-bold mb-3">{game}</h3>
              <div className="flex gap-2">
                <button className="flex-1 bg-pink-600 hover:bg-pink-700 px-4 py-2 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2">
                  <Play className="w-4 h-4" />
                  Play Now
                </button>
                <button className="bg-gray-800 hover:bg-gray-700 px-4 py-2 rounded-lg transition-colors">
                  <Code className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Featured Section */}
        <div className="mt-12 bg-gradient-to-r from-purple-900/30 to-pink-900/30 border border-purple-700/50 rounded-lg p-8">
          <div className="flex items-center gap-3 mb-4">
            <ExternalLink className="w-6 h-6 text-pink-400" />
            <h2 className="text-2xl font-semibold">Embed Games on Your Site</h2>
          </div>
          <p className="text-gray-400 mb-4">
            Get embed codes for all games and integrate them into your website
          </p>
          <button className="bg-pink-600 hover:bg-pink-700 px-6 py-3 rounded-lg font-semibold transition-colors">
            Get Embed Codes
          </button>
        </div>
      </div>
    </div>
  );
};

export default WebGamesHub;
