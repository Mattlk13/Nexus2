import React, { useState, useEffect } from 'react';
import { Heart, MessageCircle, Share2, Send, Image, Video, Music, Plus, TrendingUp } from 'lucide-react';
import axios from 'axios';
import { useAuth, API } from '../App';
import { toast } from 'sonner';

const Newsfeed = () => {
  const { token, user } = useAuth();
  const [posts, setPosts] = useState([]);
  const [newPost, setNewPost] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedPost, setSelectedPost] = useState(null);
  const [comments, setComments] = useState({});
  const [commentText, setCommentText] = useState('');

  useEffect(() => {
    loadPosts();
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadPosts, 30000);
    return () => clearInterval(interval);
  }, [token]);

  const loadPosts = async () => {
    try {
      const response = await axios.get(`${API}/newsfeed/posts`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });
      setPosts(response.data.posts || []);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load posts:', err);
      setLoading(false);
    }
  };

  const createPost = async () => {
    if (!newPost.trim()) {
      toast.error('Please enter something to post');
      return;
    }
    
    if (!token) {
      toast.error('Please sign in to create posts');
      return;
    }
    
    try {
      await axios.post(
        `${API}/newsfeed/posts`,
        { content: newPost },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setNewPost('');
      toast.success('Post created!');
      loadPosts();
    } catch (err) {
      console.error('Failed to create post:', err);
      toast.error('Failed to create post');
    }
  };

  const likePost = async (postId) => {
    if (!token) {
      toast.error('Please sign in to like posts');
      return;
    }
    
    try {
      await axios.post(
        `${API}/newsfeed/posts/${postId}/like`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      loadPosts();
    } catch (err) {
      console.error('Failed to like post:', err);
      toast.error('Failed to like post');
    }
  };

  const loadComments = async (postId) => {
    try {
      const response = await axios.get(`${API}/newsfeed/posts/${postId}/comments`);
      setComments({ ...comments, [postId]: response.data.comments || [] });
      setSelectedPost(postId);
    } catch (err) {
      console.error('Failed to load comments:', err);
    }
  };

  const addComment = async (postId) => {
    if (!commentText.trim()) return;
    if (!token) {
      toast.error('Please sign in to comment');
      return;
    }
    
    try {
      await axios.post(
        `${API}/newsfeed/posts/${postId}/comment`,
        { content: commentText },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setCommentText('');
      toast.success('Comment added!');
      loadComments(postId);
      loadPosts();
    } catch (err) {
      console.error('Failed to add comment:', err);
      toast.error('Failed to add comment');
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-24">
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Sidebar - Quick Links */}
          <div className="hidden lg:block lg:col-span-3">
            <div className="sticky top-24 space-y-4">
              <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-4">
                <h3 className="font-bold mb-4 text-lg">Quick Access</h3>
                <div className="space-y-2">
                  <a href="/creation-studio" className="w-full flex items-center gap-3 p-3 hover:bg-white/5 rounded-xl transition-all">
                    <Music className="w-5 h-5 text-cyan-400" />
                    <span>Creation Studio</span>
                  </a>
                  <a href="/marketplace" className="w-full flex items-center gap-3 p-3 hover:bg-white/5 rounded-xl transition-all">
                    <TrendingUp className="w-5 h-5 text-purple-400" />
                    <span>Marketplace</span>
                  </a>
                </div>
              </div>
            </div>
          </div>

          {/* Center Feed */}
          <div className="lg:col-span-6 space-y-6">
            {/* Create Post */}
            {user && (
              <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-purple-500 rounded-full flex items-center justify-center font-bold">
                    {user.username?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <div className="flex-1">
                    <textarea
                      value={newPost}
                      onChange={(e) => setNewPost(e.target.value)}
                      placeholder="What's on your mind?"
                      className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 resize-none focus:outline-none focus:border-cyan-500 transition-all"
                      rows="3"
                    />
                    <div className="flex items-center justify-between mt-4">
                      <div className="flex gap-2">
                        <button className="p-2 hover:bg-white/5 rounded-lg transition-all" title="Coming soon">
                          <Image className="w-5 h-5 text-green-400" />
                        </button>
                        <button className="p-2 hover:bg-white/5 rounded-lg transition-all" title="Coming soon">
                          <Video className="w-5 h-5 text-blue-400" />
                        </button>
                      </div>
                      <button
                        onClick={createPost}
                        disabled={!newPost.trim()}
                        className="px-6 py-2 bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-700 hover:to-purple-700 rounded-xl font-semibold flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Send className="w-4 h-4" />
                        Post
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Posts Feed */}
            <div className="space-y-6">
              {loading ? (
                <div className="text-center py-12 text-gray-400">Loading posts...</div>
              ) : posts.length === 0 ? (
                <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-12 text-center">
                  <p className="text-gray-400 mb-4">No posts yet. Be the first to share!</p>
                  {user && (
                    <button 
                      onClick={() => document.querySelector('textarea')?.focus()}
                      className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-purple-600 rounded-xl font-semibold flex items-center gap-2 mx-auto"
                    >
                      <Plus className="w-5 h-5" />
                      Create First Post
                    </button>
                  )}
                </div>
              ) : (
                posts.map((post) => (
                  <div key={post.id} className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:border-cyan-500/30 transition-all">
                    {/* Post Header */}
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-purple-500 rounded-full flex items-center justify-center font-bold">
                        {post.author_name?.charAt(0).toUpperCase() || 'U'}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold">{post.author_name || 'User'}</h3>
                        <p className="text-sm text-gray-400">
                          {new Date(post.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>

                    {/* Post Content */}
                    <p className="text-gray-200 mb-4 leading-relaxed whitespace-pre-wrap">{post.content}</p>

                    {/* Post Actions */}
                    <div className="flex items-center gap-6 pt-4 border-t border-white/10">
                      <button
                        onClick={() => likePost(post.id)}
                        className={`flex items-center gap-2 transition-all ${
                          post.liked_by_user ? 'text-pink-400' : 'text-gray-400 hover:text-pink-400'
                        }`}
                      >
                        <Heart className={`w-5 h-5 ${post.liked_by_user ? 'fill-pink-400' : ''}`} />
                        <span>{post.likes || 0}</span>
                      </button>
                      <button 
                        onClick={() => loadComments(post.id)}
                        className="flex items-center gap-2 text-gray-400 hover:text-cyan-400 transition-all"
                      >
                        <MessageCircle className="w-5 h-5" />
                        <span>{post.comments || 0}</span>
                      </button>
                      <button className="flex items-center gap-2 text-gray-400 hover:text-green-400 transition-all">
                        <Share2 className="w-5 h-5" />
                        <span>Share</span>
                      </button>
                    </div>

                    {/* Comments Section */}
                    {selectedPost === post.id && (
                      <div className="mt-4 pt-4 border-t border-white/10 space-y-4">
                        {/* Comment Input */}
                        {user && (
                          <div className="flex gap-3">
                            <input
                              type="text"
                              value={commentText}
                              onChange={(e) => setCommentText(e.target.value)}
                              onKeyPress={(e) => e.key === 'Enter' && addComment(post.id)}
                              placeholder="Write a comment..."
                              className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-cyan-500"
                            />
                            <button
                              onClick={() => addComment(post.id)}
                              disabled={!commentText.trim()}
                              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg disabled:opacity-50 transition-all"
                            >
                              <Send className="w-4 h-4" />
                            </button>
                          </div>
                        )}

                        {/* Comments List */}
                        <div className="space-y-3">
                          {(comments[post.id] || []).map((comment) => (
                            <div key={comment.id} className="flex gap-3 p-3 bg-white/5 rounded-lg">
                              <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-purple-500 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0">
                                {comment.author_name?.charAt(0).toUpperCase() || 'U'}
                              </div>
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="font-semibold text-sm">{comment.author_name}</span>
                                  <span className="text-xs text-gray-500">
                                    {new Date(comment.created_at).toLocaleString()}
                                  </span>
                                </div>
                                <p className="text-sm text-gray-300">{comment.content}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Right Sidebar - Trending & Suggestions */}
          <div className="hidden lg:block lg:col-span-3">
            <div className="sticky top-24 space-y-4">
              <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-4">
                <h3 className="font-bold mb-4 text-lg">Trending Now</h3>
                <div className="space-y-3">
                  {['#AIMusic', '#DigitalArt', '#NFTMarket', '#CreatorEconomy'].map((tag, idx) => (
                    <div key={idx} className="flex items-center justify-between p-2 hover:bg-white/5 rounded-lg transition-all cursor-pointer">
                      <span className="text-cyan-400 font-semibold">{tag}</span>
                      <span className="text-xs text-gray-400">{Math.floor(Math.random() * 10)}k posts</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Newsfeed;
