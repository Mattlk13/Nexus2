import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';
import { toast } from 'sonner';
import { Share2, Calendar, Image, Send, CheckCircle, AlertCircle } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

export const SocialMediaManagerPage = () => {
  const { user, token } = useAuth();
  const [status, setStatus] = useState(null);
  const [postContent, setPostContent] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [mediaUrl, setMediaUrl] = useState('');
  const [scheduleDate, setScheduleDate] = useState('');
  const [posting, setPosting] = useState(false);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const res = await axios.get(`${API}/social-media/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStatus(res.data);
    } catch (err) {
      console.error('Status fetch error:', err);
    }
  };

  const handlePost = async () => {
    if (!postContent.trim()) {
      toast.error('Please enter post content');
      return;
    }

    if (selectedPlatforms.length === 0) {
      toast.error('Please select at least one platform');
      return;
    }

    setPosting(true);
    try {
      const payload = {
        text: postContent,
        media_url: mediaUrl || null,
        platforms: selectedPlatforms,
        scheduled_at: scheduleDate || null
      };

      const res = await axios.post(`${API}/social-media/post`, payload, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (res.data.success) {
        toast.success(`✓ Posted to ${res.data.platforms_posted} platform(s)!`);
        setPostContent('');
        setMediaUrl('');
        setScheduleDate('');
        setSelectedPlatforms([]);
      } else {
        toast.error('Post failed');
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Post failed');
    } finally {
      setPosting(false);
    }
  };

  const togglePlatform = (platform) => {
    setSelectedPlatforms(prev =>
      prev.includes(platform)
        ? prev.filter(p => p !== platform)
        : [...prev, platform]
    );
  };

  if (!status) {
    return (
      <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="animate-pulse text-white/60">Loading...</div>
        </div>
      </div>
    );
  }

  const platforms = status.platforms || {};

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="font-rajdhani text-4xl md:text-5xl font-bold mb-4">
            <span className="gradient-text">Social Media Manager</span>
          </h1>
          <p className="text-white/60">Post to multiple platforms at once</p>
        </div>

        {/* Platform Status */}
        <div className="glass rounded-xl p-6 mb-8">
          <h2 className="text-xl font-rajdhani font-semibold mb-4 flex items-center gap-2">
            <Share2 className="w-5 h-5" />
            Connected Platforms ({status.active_count}/{status.total_count})
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(platforms).map(([key, platform]) => (
              <div
                key={key}
                className={`p-4 rounded-lg border ${
                  platform.active
                    ? 'bg-green-500/10 border-green-500/30'
                    : 'bg-white/5 border-white/10'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-white">{platform.name}</h3>
                  {platform.active ? (
                    <CheckCircle className="w-5 h-5 text-green-400" />
                  ) : (
                    <AlertCircle className="w-5 h-5 text-white/40" />
                  )}
                </div>
                <p className="text-xs text-white/60">
                  {platform.active ? 'Connected' : 'Not configured'}
                </p>
                {platform.active && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {platform.features.map(feature => (
                      <span
                        key={feature}
                        className="text-xs px-2 py-0.5 bg-cyan-500/20 text-cyan-400 rounded"
                      >
                        {feature.replace('_', ' ')}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {status.active_count === 0 && (
            <div className="mt-6 p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
              <p className="text-sm text-yellow-400">
                ⚠️ No social media platforms configured. Add API keys in Settings to enable posting.
              </p>
            </div>
          )}
        </div>

        {/* Post Composer */}
        <div className="glass rounded-xl p-6 md:p-8">
          <h2 className="text-xl font-rajdhani font-semibold mb-6">Create Post</h2>

          {/* Post Content */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-white/60 mb-2">
              Post Content
            </label>
            <textarea
              value={postContent}
              onChange={(e) => setPostContent(e.target.value)}
              placeholder="What would you like to share?"
              rows={6}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-cyan-500/50 focus:outline-none text-white placeholder:text-white/30 resize-none"
            />
            <div className="flex items-center justify-between mt-2">
              <span className="text-xs text-white/40">
                {postContent.length} characters
              </span>
            </div>
          </div>

          {/* Media URL */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-white/60 mb-2 flex items-center gap-2">
              <Image className="w-4 h-4" />
              Media URL (Optional)
            </label>
            <input
              type="text"
              value={mediaUrl}
              onChange={(e) => setMediaUrl(e.target.value)}
              placeholder="https://example.com/image.jpg"
              className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:border-cyan-500/50 focus:outline-none text-white placeholder:text-white/30"
            />
          </div>

          {/* Schedule Date */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-white/60 mb-2 flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Schedule (Optional)
            </label>
            <input
              type="datetime-local"
              value={scheduleDate}
              onChange={(e) => setScheduleDate(e.target.value)}
              className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:border-cyan-500/50 focus:outline-none text-white"
            />
            <p className="text-xs text-white/40 mt-1">
              Leave empty to post immediately
            </p>
          </div>

          {/* Platform Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-white/60 mb-3">
              Select Platforms
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {Object.entries(platforms).map(([key, platform]) => (
                <button
                  key={key}
                  onClick={() => platform.active && togglePlatform(key)}
                  disabled={!platform.active}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    selectedPlatforms.includes(key)
                      ? 'bg-cyan-500/20 border-cyan-500'
                      : 'border-white/10 hover:border-white/30'
                  } ${
                    !platform.active && 'opacity-40 cursor-not-allowed'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-white">
                      {platform.name}
                    </span>
                    {selectedPlatforms.includes(key) && (
                      <CheckCircle className="w-4 h-4 text-cyan-400" />
                    )}
                  </div>
                  <p className="text-xs text-white/60">
                    {platform.active ? 'Ready' : 'Not connected'}
                  </p>
                </button>
              ))}
            </div>
          </div>

          {/* Post Button */}
          <button
            onClick={handlePost}
            disabled={posting || status.active_count === 0}
            className="w-full btn-primary py-4 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {posting ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Posting...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                {scheduleDate ? 'Schedule Post' : 'Post Now'}
              </>
            )}
          </button>
        </div>

        {/* Tips */}
        <div className="mt-8 glass rounded-xl p-6">
          <h3 className="font-semibold text-white mb-3">💡 Tips</h3>
          <ul className="space-y-2 text-sm text-white/60">
            <li>• Connect your platforms in Settings to enable posting</li>
            <li>• Add media URLs from your Creator Studio generated content</li>
            <li>• Use scheduling to plan your content calendar ahead</li>
            <li>• Each platform has character limits and formatting rules</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SocialMediaManagerPage;
