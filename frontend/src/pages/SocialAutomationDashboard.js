import React, { useState, useEffect } from 'react';
import { Calendar, TrendingUp, MessageSquare, Users, Share2, BarChart3, Clock, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';
import axios from 'axios';
import { useAuth, API } from '../App';

const SocialAutomationDashboard = () => {
  const { token } = useAuth();
  const [status, setStatus] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [scheduledPosts, setScheduledPosts] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('calendar');

  useEffect(() => {
    loadDashboard();
    const interval = setInterval(loadDashboard, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboard = async () => {
    try {
      const [statusRes, analyticsRes, postsRes, convoRes] = await Promise.all([
        axios.get(`${API}/api/social-automation/status`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/api/social-automation/analytics`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/api/social-automation/scheduled-posts`, { headers: { Authorization: `Bearer ${token}` } }),
        axios.get(`${API}/api/social-automation/conversations`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      
      setStatus(statusRes.data);
      setAnalytics(analyticsRes.data);
      setScheduledPosts(postsRes.data.scheduled_posts || []);
      setConversations(convoRes.data.conversations || []);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
      setLoading(false);
    }
  };

  const scheduleContent = async () => {
    try {
      await axios.post(
        `${API}/api/social-automation/schedule`,
        { days_ahead: 30 },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('✅ 30 days of content scheduled!');
      loadDashboard();
    } catch (err) {
      alert('Failed to schedule content');
    }
  };

  const publishPost = async (postId) => {
    try {
      await axios.post(
        `${API}/api/social-automation/publish/${postId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('✅ Post published!');
      loadDashboard();
    } catch (err) {
      alert('Failed to publish post');
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
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                Social Automation Hub
              </h1>
              <p className="text-gray-400 mt-1">AI-powered social media management across all platforms</p>
            </div>
            <button
              onClick={scheduleContent}
              className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-700 hover:to-purple-700 rounded-xl font-semibold flex items-center gap-2 transition-all"
            >
              <Calendar className="w-5 h-5" />
              Generate 30 Days
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-cyan-500/20 rounded-xl">
                <Calendar className="w-6 h-6 text-cyan-400" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Scheduled Posts</p>
                <p className="text-2xl font-bold">{status?.scheduled_posts || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-500/20 rounded-xl">
                <CheckCircle className="w-6 h-6 text-green-400" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Published</p>
                <p className="text-2xl font-bold">{analytics?.total_posts || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-500/20 rounded-xl">
                <TrendingUp className="w-6 h-6 text-purple-400" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Total Reach</p>
                <p className="text-2xl font-bold">{analytics?.total_reach?.toLocaleString() || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-orange-500/20 rounded-xl">
                <Users className="w-6 h-6 text-orange-400" />
              </div>
              <div>
                <p className="text-gray-400 text-sm">Follower Growth</p>
                <p className="text-2xl font-bold">+{analytics?.follower_growth || 0}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          {['calendar', 'analytics', 'conversations'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 rounded-xl font-semibold capitalize transition-all ${
                activeTab === tab
                  ? 'bg-gradient-to-r from-cyan-600 to-purple-600 text-white'
                  : 'bg-white/5 text-gray-400 hover:bg-white/10'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Content Area */}
        {activeTab === 'calendar' && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold mb-4">Scheduled Content</h2>
            {scheduledPosts.length === 0 ? (
              <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-12 text-center">
                <Calendar className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400 mb-4">No content scheduled yet</p>
                <button
                  onClick={scheduleContent}
                  className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-purple-600 rounded-xl font-semibold"
                >
                  Generate 30 Days of Content
                </button>
              </div>
            ) : (
              scheduledPosts.map((post) => (
                <div key={post.id} className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold mb-2">{post.topic}</h3>
                      <div className="flex items-center gap-4 text-sm text-gray-400">
                        <span className="flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          {post.scheduled_for}
                        </span>
                        <span className="flex items-center gap-1">
                          <Share2 className="w-4 h-4" />
                          {post.platforms?.length || 0} platforms
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => publishPost(post.id)}
                      className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg font-semibold transition-all"
                    >
                      Publish Now
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'analytics' && analytics && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold mb-4">Performance Analytics</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
                <h3 className="text-lg font-semibold mb-4">Engagement Overview</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Engagement Rate</span>
                    <span className="text-2xl font-bold text-green-400">{analytics.engagement_rate}%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Total Clicks</span>
                    <span className="text-xl font-bold">{analytics.clicks}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Impressions</span>
                    <span className="text-xl font-bold">{analytics.total_impressions?.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
                <h3 className="text-lg font-semibold mb-4">Best Platform</h3>
                <div className="text-center py-4">
                  <p className="text-4xl font-bold capitalize bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                    {analytics.best_performing_platform}
                  </p>
                  <p className="text-gray-400 mt-2">Highest engagement</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'conversations' && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold mb-4">Social Listening</h2>
            {conversations.length === 0 ? (
              <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-12 text-center">
                <MessageSquare className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">No conversations found yet</p>
                <p className="text-sm text-gray-500 mt-2">We're monitoring Reddit, X, and Facebook for relevant discussions</p>
              </div>
            ) : (
              conversations.map((conv) => (
                <div key={conv.id} className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="px-3 py-1 bg-cyan-500/20 text-cyan-400 rounded-full text-sm font-semibold">
                          {conv.platform}
                        </span>
                        <span className="text-gray-400 text-sm">Relevance: {(conv.relevance_score * 100).toFixed(0)}%</span>
                      </div>
                      <p className="text-gray-300 mb-2">{conv.text}</p>
                      <a
                        href={conv.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-cyan-400 hover:text-cyan-300 text-sm"
                      >
                        View conversation →
                      </a>
                    </div>
                    <button className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition-all">
                      Engage
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SocialAutomationDashboard;