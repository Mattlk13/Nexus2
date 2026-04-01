import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Edit, MapPin, Link as LinkIcon, Calendar, Mail, Users, Image as ImageIcon } from 'lucide-react';

const Profile = () => {
  const [editing, setEditing] = useState(false);
  const [profile, setProfile] = useState({
    fullName: 'John Doe',
    username: '@johndoe',
    bio: 'AI enthusiast | Creator | Building the future with NEXUS',
    location: 'San Francisco, CA',
    website: 'johndoe.com',
    email: 'john@example.com',
    joinDate: 'January 2026',
    avatar: '👤'
  });

  const [stats] = useState({
    posts: 142,
    friends: 1234,
    followers: 5678,
    following: 890
  });

  const [posts] = useState([
    { id: 1, content: 'Just created an amazing AI video using NEXUS Creation Studio! 🎥✨', likes: 45, comments: 12, time: '2h ago' },
    { id: 2, content: 'The marketplace feature is incredible. Already made 3 sales today! 💰', likes: 78, comments: 23, time: '5h ago' },
    { id: 3, content: 'Anyone else excited about the new AI features? This platform is revolutionary!', likes: 156, comments: 45, time: '1d ago' },
  ]);

  const handleSave = () => {
    setEditing(false);
    // Save to backend
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Cover Photo */}
      <div className="h-64 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 relative">
        <Button
          variant="secondary"
          size="sm"
          className="absolute bottom-4 right-4"
        >
          <ImageIcon className="h-4 w-4 mr-2" />
          Change Cover
        </Button>
      </div>

      <div className="max-w-5xl mx-auto px-4 -mt-32">
        
        {/* Profile Header */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row items-start md:items-center space-y-4 md:space-y-0 md:space-x-6">
              
              {/* Avatar */}
              <div className="relative">
                <div className="h-32 w-32 rounded-full bg-gradient-to-br from-blue-400 to-purple-600 flex items-center justify-center text-6xl border-4 border-white shadow-xl">
                  {profile.avatar}
                </div>
                <Button
                  variant="secondary"
                  size="sm"
                  className="absolute bottom-0 right-0 rounded-full"
                >
                  <ImageIcon className="h-4 w-4" />
                </Button>
              </div>

              {/* Info */}
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h1 className="text-3xl font-bold">{profile.fullName}</h1>
                    <p className="text-gray-600">{profile.username}</p>
                  </div>
                  {!editing ? (
                    <Button onClick={() => setEditing(true)}>
                      <Edit className="h-4 w-4 mr-2" />
                      Edit Profile
                    </Button>
                  ) : (
                    <div className="space-x-2">
                      <Button variant="outline" onClick={() => setEditing(false)}>
                        Cancel
                      </Button>
                      <Button onClick={handleSave}>
                        Save Changes
                      </Button>
                    </div>
                  )}
                </div>

                {editing ? (
                  <div className="space-y-3 mt-4">
                    <Input
                      value={profile.fullName}
                      onChange={(e) => setProfile({ ...profile, fullName: e.target.value })}
                      placeholder="Full name"
                    />
                    <Textarea
                      value={profile.bio}
                      onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                      placeholder="Bio"
                      rows={3}
                    />
                    <div className="grid grid-cols-2 gap-3">
                      <Input
                        value={profile.location}
                        onChange={(e) => setProfile({ ...profile, location: e.target.value })}
                        placeholder="Location"
                      />
                      <Input
                        value={profile.website}
                        onChange={(e) => setProfile({ ...profile, website: e.target.value })}
                        placeholder="Website"
                      />
                    </div>
                  </div>
                ) : (
                  <>
                    <p className="text-gray-700 mb-4">{profile.bio}</p>
                    <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                      <div className="flex items-center">
                        <MapPin className="h-4 w-4 mr-1" />
                        {profile.location}
                      </div>
                      <div className="flex items-center">
                        <LinkIcon className="h-4 w-4 mr-1" />
                        <a href={`https://${profile.website}`} className="text-blue-600 hover:underline">
                          {profile.website}
                        </a>
                      </div>
                      <div className="flex items-center">
                        <Mail className="h-4 w-4 mr-1" />
                        {profile.email}
                      </div>
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 mr-1" />
                        Joined {profile.joinDate}
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-4 gap-4 mt-6 pt-6 border-t">
              <div className="text-center">
                <p className="text-2xl font-bold">{stats.posts}</p>
                <p className="text-sm text-gray-600">Posts</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">{stats.friends}</p>
                <p className="text-sm text-gray-600">Friends</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">{stats.followers}</p>
                <p className="text-sm text-gray-600">Followers</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">{stats.following}</p>
                <p className="text-sm text-gray-600">Following</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Posts */}
        <div className="space-y-4 pb-8">
          <h2 className="text-xl font-bold">Posts</h2>
          {posts.map(post => (
            <Card key={post.id}>
              <CardContent className="pt-6">
                <p className="mb-4">{post.content}</p>
                <div className="flex items-center space-x-6 text-sm text-gray-600">
                  <button className="hover:text-red-600">❤️ {post.likes} Likes</button>
                  <button className="hover:text-blue-600">💬 {post.comments} Comments</button>
                  <span>{post.time}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Profile;
