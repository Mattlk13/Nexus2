import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { 
  Brain, Music, Code, Shield, Users, Zap, Database, 
  Boxes, Gamepad2, Eye, Palette, Radio, Package, GitBranch,
  Loader2, ExternalLink, Star, Sparkles
} from 'lucide-react';
import { API } from '../App';

const AllHybridsShowcase = () => {
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Fetch controller status
  const { data: controllerStatus, isLoading } = useQuery({
    queryKey: ['controller-status'],
    queryFn: async () => {
      const res = await axios.get(`${API}/hybrid/controller/status`);
      return res.data;
    }
  });

  const hybridPages = [
    { id: 'ml', name: 'ML Studio', path: '/ml-studio', icon: Brain, color: 'from-blue-400 to-cyan-500', category: 'ai' },
    { id: 'music', name: 'Music Studio', path: '/music-studio', icon: Music, color: 'from-purple-400 to-pink-500', category: 'ai' },
    { id: 'claude', name: 'Claude AI', path: '/admin', icon: Sparkles, color: 'from-violet-400 to-purple-500', category: 'ai' },
    { id: 'ai_models', name: 'AI Model Zoos', path: '/ai-models', icon: Database, color: 'from-blue-400 to-indigo-500', category: 'ai' },
    { id: 'netneutrality', name: 'Net Neutrality', path: '/net-neutrality', icon: Shield, color: 'from-green-400 to-emerald-500', category: 'advocacy' },
    { id: 'devtools', name: 'Dev Tools', path: '/dev-tools', icon: Code, color: 'from-purple-400 to-indigo-500', category: 'development' },
    { id: 'opensource', name: 'Open Source Tools', path: '/opensource', icon: Package, color: 'from-green-400 to-blue-500', category: 'automation' },
    { id: 'accessibility', name: 'Accessibility', path: '/accessibility', icon: Eye, color: 'from-blue-400 to-green-500', category: 'inclusive' },
    { id: 'js_state', name: 'JS State Management', path: '/js-state', icon: Boxes, color: 'from-cyan-400 to-blue-500', category: 'frontend' },
    { id: 'php_quality', name: 'PHP Code Quality', path: '/php-quality', icon: Code, color: 'from-indigo-400 to-purple-500', category: 'development' },
    { id: 'webgames', name: 'Web Games', path: '/web-games', icon: Gamepad2, color: 'from-pink-400 to-purple-500', category: 'gaming' },
    { id: 'probot', name: 'GitHub Probot Apps', path: '/opensource', icon: GitBranch, color: 'from-gray-400 to-blue-500', category: 'automation' },
  ];

  const categories = [
    { id: 'all', label: 'All Hybrids', count: 32 },
    { id: 'ai', label: 'AI & ML', count: 6 },
    { id: 'development', label: 'Development', count: 8 },
    { id: 'automation', label: 'Automation', count: 7 },
    { id: 'community', label: 'Community', count: 6 },
    { id: 'security', label: 'Security', count: 5 }
  ];

  const filteredHybrids = selectedCategory === 'all' 
    ? hybridPages 
    : hybridPages.filter(h => h.category === selectedCategory);

  if (isLoading) {
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
        <div className="mb-12 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border border-cyan-500/20 rounded-full mb-4">
            <Zap className="w-5 h-5 text-cyan-400" />
            <span className="text-sm font-semibold text-cyan-400">
              {controllerStatus?.total_hybrids || 32} Active Hybrid Systems
            </span>
          </div>
          
          <h1 className="text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-500 bg-clip-text text-transparent">
              NEXUS Hybrid Integrations
            </span>
          </h1>
          
          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
            Autonomous Integration Engine that combines 100+ open-source tools into powerful hybrid systems
          </p>

          {/* Stats */}
          <div className="flex gap-6 justify-center flex-wrap">
            <div className="px-6 py-4 bg-white/5 rounded-xl backdrop-blur">
              <div className="text-3xl font-bold text-cyan-400">{controllerStatus?.total_hybrids || 32}</div>
              <div className="text-sm text-gray-400">Active Hybrids</div>
            </div>
            <div className="px-6 py-4 bg-white/5 rounded-xl backdrop-blur">
              <div className="text-3xl font-bold text-purple-400">100+</div>
              <div className="text-sm text-gray-400">Integrated Services</div>
            </div>
            <div className="px-6 py-4 bg-white/5 rounded-xl backdrop-blur">
              <div className="text-3xl font-bold text-green-400">700k+</div>
              <div className="text-sm text-gray-400">Combined Stars</div>
            </div>
            <div className="px-6 py-4 bg-white/5 rounded-xl backdrop-blur">
              <div className="text-3xl font-bold text-yellow-400">20+</div>
              <div className="text-sm text-gray-400">External APIs</div>
            </div>
          </div>
        </div>

        {/* Category Filters */}
        <div className="flex gap-2 mb-8 overflow-x-auto pb-2\">
          {categories.map(cat => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-4 py-2 rounded-lg font-semibold whitespace-nowrap transition-all ${
                selectedCategory === cat.id
                  ? 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white'
                  : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              {cat.label} <span className="text-xs ml-1">({cat.count})</span>
            </button>
          ))}
        </div>

        {/* Hybrids Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredHybrids.map((hybrid) => {
            const IconComponent = hybrid.icon;
            return (
              <Link
                key={hybrid.id}
                to={hybrid.path}
                className="group bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 hover:border-cyan-400/50 rounded-lg p-6 transition-all transform hover:scale-105"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${hybrid.color} flex items-center justify-center`}>
                    <IconComponent className="w-6 h-6 text-white" />
                  </div>
                  <ExternalLink className="w-5 h-5 text-gray-500 group-hover:text-cyan-400 transition-colors" />
                </div>
                <h3 className="text-xl font-bold mb-2 group-hover:text-cyan-400 transition-colors">
                  {hybrid.name}
                </h3>
                <p className="text-gray-400 text-sm capitalize">{hybrid.category}</p>
              </Link>
            );
          })}
        </div>

        {/* System Status */}
        {controllerStatus && (
          <div className="mt-12 bg-gradient-to-r from-cyan-900/20 to-purple-900/20 border border-cyan-700/50 rounded-lg p-8">
            <h2 className="text-2xl font-semibold mb-4">System Status</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-800/50 rounded-lg p-4">
                <p className="text-3xl font-bold text-cyan-400">{controllerStatus.total_hybrids}</p>
                <p className="text-sm text-gray-400">Total Hybrids</p>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4">
                <p className="text-3xl font-bold text-green-400">{controllerStatus.active_hybrids}</p>
                <p className="text-sm text-gray-400">Active</p>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4">
                <p className="text-3xl font-bold text-purple-400">{Object.keys(controllerStatus.by_category || {}).length}</p>
                <p className="text-sm text-gray-400">Categories</p>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4">
                <p className="text-3xl font-bold text-yellow-400">{controllerStatus.status === 'operational' ? '100%' : '0%'}</p>
                <p className="text-sm text-gray-400">Uptime</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AllHybridsShowcase;
