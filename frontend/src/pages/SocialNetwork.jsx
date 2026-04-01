import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Heart, MessageCircle, Share2, Send, Users, Bell } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const SocialNetwork = () => {
  const [user] = useState({ id: 'demo-1', username: 'demo', full_name: 'Demo User' });
  const [newsFeed, setNewsFeed] = useState([]);
  const [newPost, setNewPost] = useState('');
  const [activeTab, setActiveTab] = useState('feed');

  const Avatar = ({ name, size = 'md' }) => {
    const sizes = { sm: 'h-8 w-8 text-sm', md: 'h-10 w-10', lg: 'h-16 w-16 text-lg' };
    return (
      <div className={`${sizes[size]} rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold`}>
        {name?.[0]?.toUpperCase() || 'U'}
      </div>
    );
  };

  const createPost = () => {
    if (!newPost.trim()) return;
    
    const post = {
      id: Date.now().toString(),
      user_id: user.id,
      user: user,
      content: newPost,
      likes: [],
      comments: [],
      created_at: new Date().toISOString()
    };
    
    setNewsFeed([post, ...newsFeed]);
    setNewPost('');
  };

  const likePost = (postId) => {
    setNewsFeed(newsFeed.map(post => 
      post.id === postId 
        ? { 
            ...post, 
            likes: post.likes.includes(user.id) 
              ? post.likes.filter(id => id !== user.id)
              : [...post.likes, user.id]
          }
        : post
    ));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white border-b sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              NEXUS Social
            </h1>
            
            <div className="flex items-center space-x-4">
              <Button
                variant={activeTab === 'feed' ? 'default' : 'ghost'}
                onClick={() => setActiveTab('feed')}
              >
                Feed
              </Button>
              <Button
                variant={activeTab === 'friends' ? 'default' : 'ghost'}
                onClick={() => setActiveTab('friends')}
              >
                <Users className="h-4 w-4 mr-2" />
                Friends
              </Button>
              <Button variant="ghost" size="icon">
                <Bell className="h-5 w-5" />
              </Button>
              <Avatar name={user.username} />
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {activeTab === 'feed' && (
          <>
            {/* Post Composer */}
            <Card className="mb-6">
              <CardContent className="pt-6">
                <div className="flex space-x-4">
                  <Avatar name={user.username} size="lg" />
                  <div className="flex-1">
                    <Textarea
                      placeholder="What's on your mind?"
                      value={newPost}
                      onChange={(e) => setNewPost(e.target.value)}
                      className="mb-4 resize-none"
                      rows={3}
                    />
                    <div className="flex justify-between items-center">
                      <div className="flex space-x-2">
                        <Button variant="ghost" size="sm">📷 Photo</Button>
                        <Button variant="ghost" size="sm">🎥 Video</Button>
                        <Button variant="ghost" size="sm">✨ AI Generate</Button>
                      </div>
                      <Button onClick={createPost} disabled={!newPost.trim()}>
                        Post
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* News Feed */}
            <div className="space-y-6">
              {newsFeed.map(post => (
                <Card key={post.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-center space-x-3">
                      <Avatar name={post.user?.username} />
                      <div>
                        <p className="font-semibold">{post.user?.full_name || 'Unknown User'}</p>
                        <p className="text-sm text-gray-500">
                          {new Date(post.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="mb-4 text-gray-800">{post.content}</p>
                    
                    {/* Post Actions */}
                    <div className="flex items-center space-x-6 pt-4 border-t">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => likePost(post.id)}
                        className={post.likes?.includes(user?.id) ? 'text-red-500' : ''}
                      >
                        <Heart className={`h-4 w-4 mr-2 ${post.likes?.includes(user?.id) ? 'fill-current' : ''}`} />
                        {post.likes?.length || 0} Likes
                      </Button>
                      <Button variant="ghost" size="sm">
                        <MessageCircle className="h-4 w-4 mr-2" />
                        {post.comments?.length || 0} Comments
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Share2 className="h-4 w-4 mr-2" />
                        Share
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}

              {newsFeed.length === 0 && (
                <Card className="text-center py-12">
                  <CardContent>
                    <div className="text-6xl mb-4">📝</div>
                    <h3 className="text-xl font-semibold mb-2">No posts yet!</h3>
                    <p className="text-gray-500 mb-4">
                      Be the first to share something with the world.
                    </p>
                    <p className="text-sm text-gray-400">
                      This is a demo of NEXUS Social Network. Backend is ready with WebSocket support!
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </>
        )}

        {activeTab === 'friends' && (
          <Card>
            <CardHeader>
              <CardTitle>Friends</CardTitle>
            </CardHeader>
            <CardContent className="text-center py-12">
              <Users className="h-16 w-16 mx-auto mb-4 text-gray-400" />
              <p className="text-gray-500">
                Friend system ready! Connect your account to see friends.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default SocialNetwork;
