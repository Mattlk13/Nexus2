import React, { useState, useEffect } from 'react';
import { Music, Video, BookOpen, Download, Share2, Eye, Play, Trash2, RefreshCw } from 'lucide-react';
import axios from 'axios';
import { useAuth, API } from '../App';

const CreatedContentPage = () => {
  const { token } = useAuth();
  const [content, setContent] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadContent();
  }, []);

  const loadContent = async () => {
    try {
      const response = await axios.get(`${API}/api/studio/created-content`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setContent(response.data.content || []);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load content:', err);
      // Mock data for demo
      setContent([
        {
          id: '1',
          type: 'music',
          title: 'Lo-fi Summer Beats',
          created_at: new Date().toISOString(),
          duration: '3:24',
          url: '/demo/music.mp3',
          thumbnail: null,
          views: 156,
          downloads: 23
        },
        {
          id: '2',
          type: 'video',
          title: 'Product Demo Animation',
          created_at: new Date(Date.now() - 86400000).toISOString(),
          duration: '0:45',
          url: '/demo/video.mp4',
          thumbnail: null,
          views: 342,
          downloads: 67
        },
        {
          id: '3',
          type: 'ebook',
          title: 'Complete Guide to Digital Marketing',
          created_at: new Date(Date.now() - 172800000).toISOString(),
          pages: 48,
          url: '/demo/ebook.pdf',
          thumbnail: null,
          views: 89,
          downloads: 12
        }
      ]);
      setLoading(false);
    }
  };

  const filteredContent = filter === 'all' 
    ? content 
    : content.filter(item => item.type === filter);

  const getIcon = (type) => {
    switch (type) {
      case 'music': return Music;
      case 'video': return Video;
      case 'ebook': return BookOpen;
      default: return Music;
    }
  };

  const getColor = (type) => {
    switch (type) {
      case 'music': return 'from-purple-500 to-pink-500';
      case 'video': return 'from-blue-500 to-cyan-500';
      case 'ebook': return 'from-orange-500 to-red-500';
      default: return 'from-purple-500 to-pink-500';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <RefreshCw className="w-12 h-12 text-cyan-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] text-white">
      {/* Header */}
      <div className="border-b border-white/10 bg-black/20 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                Created Content Library
              </h1>
              <p className="text-gray-400 mt-1">All your AI-generated creations in one place</p>
            </div>
            <div className="flex gap-3">
              <button className="px-6 py-3 bg-white/5 hover:bg-white/10 rounded-xl font-semibold flex items-center gap-2 transition-all">
                <RefreshCw className="w-5 h-5" />
                Refresh
              </button>
            </div>
          </div>

          {/* Filter Tabs */}
          <div className="flex gap-2">
            {['all', 'music', 'video', 'ebook'].map((type) => {
              const Icon = type === 'all' ? Eye : getIcon(type);
              return (
                <button
                  key={type}
                  onClick={() => setFilter(type)}
                  className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold capitalize transition-all ${
                    filter === type
                      ? 'bg-gradient-to-r from-cyan-600 to-purple-600 text-white'
                      : 'bg-white/5 text-gray-400 hover:bg-white/10'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {type}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content Grid */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {filteredContent.length === 0 ? (
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-12 text-center">
            <Music className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 mb-4">No {filter === 'all' ? '' : filter} content created yet</p>
            <a
              href="/creation-studio"
              className="inline-block px-6 py-3 bg-gradient-to-r from-cyan-600 to-purple-600 rounded-xl font-semibold"
            >
              Create Your First {filter === 'all' ? 'Content' : filter.charAt(0).toUpperCase() + filter.slice(1)}
            </a>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredContent.map((item) => {
              const Icon = getIcon(item.type);
              return (
                <div
                  key={item.id}
                  className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl overflow-hidden hover:border-cyan-500/30 transition-all group"
                >
                  {/* Thumbnail */}
                  <div className={`aspect-video bg-gradient-to-br ${getColor(item.type)} flex items-center justify-center relative`}>
                    <Icon className="w-16 h-16 text-white/50" />
                    <button className="absolute inset-0 flex items-center justify-center bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Play className="w-12 h-12 text-white" />
                    </button>
                  </div>

                  {/* Info */}
                  <div className="p-6">
                    <h3 className="text-lg font-semibold mb-2 line-clamp-2">{item.title}</h3>
                    <div className="flex items-center gap-4 text-sm text-gray-400 mb-4">
                      <span>{item.duration || `${item.pages} pages`}</span>
                      <span>•</span>
                      <span>{new Date(item.created_at).toLocaleDateString()}</span>
                    </div>

                    {/* Stats */}
                    <div className="flex items-center gap-4 text-sm text-gray-400 mb-4">
                      <span className="flex items-center gap-1">
                        <Eye className="w-4 h-4" />
                        {item.views}
                      </span>
                      <span className="flex items-center gap-1">
                        <Download className="w-4 h-4" />
                        {item.downloads}
                      </span>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                      <button className="flex-1 px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg font-semibold flex items-center justify-center gap-2 transition-all">
                        <Download className="w-4 h-4" />
                        Download
                      </button>
                      <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-all">
                        <Share2 className="w-4 h-4" />
                      </button>
                      <button className="px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition-all">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default CreatedContentPage;