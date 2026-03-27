import React, { useState } from 'react';
import { Music, Video, BookOpen, Wand2, Sparkles, Play, Download, Save, CheckCircle, ShoppingBag, Loader2 } from 'lucide-react';
import axios from 'axios';
import { useAuth, API } from '../App';
import { toast } from 'sonner';

const CreationStudio = () => {
  const { token, user } = useAuth();
  const [activeTab, setActiveTab] = useState('music');
  const [prompt, setPrompt] = useState('');
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [showPublishModal, setShowPublishModal] = useState(false);
  const [publishData, setPublishData] = useState({
    title: '',
    description: '',
    price: 9.99,
    category: 'music'
  });

  const generate = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }
    
    if (!token) {
      toast.error('Please sign in to create content');
      return;
    }
    
    setGenerating(true);
    setResult(null);
    
    try {
      const endpoint = {
        music: '/studio/generate-music',
        video: '/studio/generate-video',
        ebook: '/studio/generate-ebook'
      }[activeTab];

      const response = await axios.post(
        `${API}${endpoint}`,
        { prompt },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setResult(response.data);
      toast.success(`${activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} generated successfully!`);
    } catch (err) {
      console.error('Generation failed:', err);
      toast.error(err.response?.data?.detail || 'Generation failed. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const publishToMarketplace = async () => {
    if (!result?.id) return;
    
    try {
      const response = await axios.post(
        `${API}/studio/publish-to-marketplace`,
        {
          content_id: result.id,
          title: publishData.title,
          description: publishData.description,
          price: publishData.price,
          category: publishData.category
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast.success('Published to marketplace!');
      setShowPublishModal(false);
      setPublishData({ title: '', description: '', price: 9.99, category: activeTab });
    } catch (err) {
      console.error('Publish failed:', err);
      toast.error(err.response?.data?.detail || 'Failed to publish');
    }
  };

  const tabs = [
    { id: 'music', label: 'Music', icon: Music, color: 'from-purple-500 to-pink-500' },
    { id: 'video', label: 'Video', icon: Video, color: 'from-blue-500 to-cyan-500' },
    { id: 'ebook', label: 'eBook', icon: BookOpen, color: 'from-orange-500 to-red-500' }
  ];

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-24">
      {/* Publish Modal */}
      {showPublishModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-[#0a0a0a] border border-white/10 rounded-2xl p-8 max-w-lg w-full">
            <h2 className="text-2xl font-bold mb-6">Publish to Marketplace</h2>
            
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm font-semibold text-gray-400 mb-2">Title</label>
                <input
                  type="text"
                  value={publishData.title}
                  onChange={(e) => setPublishData({...publishData, title: e.target.value})}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500"
                  placeholder="Enter title"
                />
              </div>
              
              <div>
                <label className="block text-sm font-semibold text-gray-400 mb-2">Description</label>
                <textarea
                  value={publishData.description}
                  onChange={(e) => setPublishData({...publishData, description: e.target.value})}
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 min-h-[100px] resize-none focus:outline-none focus:border-purple-500"
                  placeholder="Describe your creation"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-400 mb-2">Price ($)</label>
                  <input
                    type="number"
                    value={publishData.price}
                    onChange={(e) => setPublishData({...publishData, price: parseFloat(e.target.value)})}
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500"
                    min="0"
                    step="0.01"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-semibold text-gray-400 mb-2">Category</label>
                  <select
                    value={publishData.category}
                    onChange={(e) => setPublishData({...publishData, category: e.target.value})}
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-purple-500"
                  >
                    <option value="music">Music</option>
                    <option value="video">Video</option>
                    <option value="ebook">eBook</option>
                    <option value="art">Art</option>
                    <option value="other">Other</option>
                  </select>
                </div>
              </div>
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={() => setShowPublishModal(false)}
                className="flex-1 px-4 py-3 bg-white/5 hover:bg-white/10 rounded-xl font-semibold transition-all"
              >
                Cancel
              </button>
              <button
                onClick={publishToMarketplace}
                disabled={!publishData.title || !publishData.description}
                className="flex-1 px-4 py-3 bg-purple-600 hover:bg-purple-700 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all disabled:opacity-50"
              >
                <ShoppingBag className="w-5 h-5" />
                Publish
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Tabs */}
        <div className="flex gap-3 mb-8 flex-wrap">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id);
                  setResult(null);
                  setPrompt('');
                }}
                className={`flex items-center gap-3 px-6 py-4 rounded-2xl font-semibold transition-all ${
                  activeTab === tab.id
                    ? `bg-gradient-to-r ${tab.color} text-white`
                    : 'bg-white/5 text-gray-400 hover:bg-white/10'
                }`}
              >
                <Icon className="w-5 h-5" />
                {tab.label}
              </button>
            );
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Panel */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <Wand2 className="w-6 h-6 text-purple-400" />
              Create {tabs.find(t => t.id === activeTab)?.label}
            </h2>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-400 mb-2">
                  Describe what you want to create
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder={
                    activeTab === 'music' ? 'E.g., "A relaxing lo-fi beat with piano and soft drums"' :
                    activeTab === 'video' ? 'E.g., "A cinematic video of a sunset over mountains"' :
                    'E.g., "A complete guide to starting a successful online business"'
                  }
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 min-h-[200px] resize-none focus:outline-none focus:border-purple-500 transition-all"
                />
              </div>

              <button
                onClick={generate}
                disabled={generating || !prompt.trim() || !token}
                className="w-full py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-xl font-bold text-lg flex items-center justify-center gap-3 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {generating ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Generate {tabs.find(t => t.id === activeTab)?.label}
                  </>
                )}
              </button>

              {!token && (
                <p className="text-sm text-yellow-400 text-center">
                  Please sign in to use the Creation Studio
                </p>
              )}
            </div>
          </div>

          {/* Result Panel */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
            <h2 className="text-2xl font-bold mb-6">Result</h2>

            {result ? (
              <div className="space-y-6">
                <div className="p-6 bg-gradient-to-br from-green-500/10 to-cyan-500/10 rounded-xl border border-green-500/20">
                  <div className="flex items-center gap-3 mb-4">
                    <CheckCircle className="w-6 h-6 text-green-400" />
                    <span className="text-green-400 font-semibold text-lg">Generated Successfully!</span>
                  </div>
                  
                  {activeTab === 'music' && (
                    <div className="prose prose-invert max-w-none">
                      <div className="text-sm text-gray-300 whitespace-pre-wrap max-h-[400px] overflow-y-auto p-4 bg-black/20 rounded-lg">
                        {result.content}
                      </div>
                    </div>
                  )}
                  
                  {activeTab === 'video' && result.video_url && (
                    <div className="space-y-3">
                      <video controls className="w-full rounded-lg bg-black">
                        <source src={result.video_url} type="video/mp4" />
                      </video>
                      <div className="text-sm text-gray-400">
                        <p>Duration: {result.duration}s</p>
                        <p>Provider: {result.provider}</p>
                      </div>
                    </div>
                  )}
                  
                  {activeTab === 'ebook' && (
                    <div className="space-y-3">
                      <div className="text-sm text-gray-300 whitespace-pre-wrap max-h-[400px] overflow-y-auto p-4 bg-black/20 rounded-lg">
                        {result.content}
                      </div>
                      <div className="text-sm text-gray-400">
                        <p>Word count: {result.word_count?.toLocaleString()}</p>
                      </div>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <button 
                    onClick={() => setShowPublishModal(true)}
                    className="px-4 py-3 bg-purple-600 hover:bg-purple-700 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all"
                  >
                    <ShoppingBag className="w-5 h-5" />
                    Publish
                  </button>
                  <button 
                    onClick={() => {
                      setResult(null);
                      setPrompt('');
                      toast.info('Ready for new creation');
                    }}
                    className="px-4 py-3 bg-white/5 hover:bg-white/10 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all"
                  >
                    <Sparkles className="w-5 h-5" />
                    New
                  </button>
                </div>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-center py-12">
                <div>
                  <Sparkles className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 mb-2">Your generated content will appear here</p>
                  <p className="text-sm text-gray-500">Enter a prompt and click Generate to start</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreationStudio;
