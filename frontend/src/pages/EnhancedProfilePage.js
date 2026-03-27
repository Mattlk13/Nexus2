import React from "react";
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import axios from "axios";
import { 
  Award, TrendingUp, Heart, Package, Users, 
  Calendar, Star, Crown, CheckCircle, Sparkles,
  DollarSign, Eye, MessageCircle
} from "lucide-react";
import { API } from "../App";

// ==================== ENHANCED USER PROFILE PAGE ====================
export const EnhancedProfilePage = () => {
  const { userId } = useParams();
  
  const { data: profile, isLoading } = useQuery({
    queryKey: ["enhanced-profile", userId],
    queryFn: () => axios.get(`${API}/users/${userId}/profile/enhanced`).then(r => r.data),
    enabled: !!userId
  });
  
  if (isLoading) {
    return (
      <div className="min-h-screen pt-20 pb-10 px-4 flex items-center justify-center">
        <div className="text-white/50">Loading profile...</div>
      </div>
    );
  }
  
  if (profile?.error) {
    return (
      <div className="min-h-screen pt-20 pb-10 px-4 flex items-center justify-center">
        <div className="text-red-400">User not found</div>
      </div>
    );
  }
  
  const user = profile?.user || {};
  const stats = profile?.statistics || {};
  const badges = profile?.badges || [];
  const portfolio = profile?.portfolio || {};
  const social = profile?.social || {};
  const insights = profile?.insights || {};
  const creatorLevel = stats.creator_level || {};
  
  return (
    <div className="min-h-screen pt-20 pb-10 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Profile Header */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl p-8 mb-8"
        >
          <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-cyan-400 to-purple-600 flex items-center justify-center text-3xl">
              {user.avatar || user.username?.charAt(0).toUpperCase() || '?'}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="font-rajdhani text-3xl font-bold">{user.username}</h1>
                {creatorLevel.level && (
                  <div className={`px-3 py-1 rounded-full font-semibold text-sm ${
                    creatorLevel.level === 'Diamond' ? 'bg-cyan-500/20 text-cyan-400' :
                    creatorLevel.level === 'Platinum' ? 'bg-purple-500/20 text-purple-400' :
                    creatorLevel.level === 'Gold' ? 'bg-yellow-500/20 text-yellow-400' :
                    creatorLevel.level === 'Silver' ? 'bg-gray-400/20 text-gray-400' :
                    'bg-orange-500/20 text-orange-400'
                  }`}>
                    <Crown className="w-4 h-4 inline mr-1" />
                    {creatorLevel.level}
                  </div>
                )}
              </div>
              <p className="text-white/70 mb-3">{user.bio || 'No bio yet'}</p>
              <div className="flex flex-wrap gap-4 text-sm text-white/60">
                <div className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  Joined {user.member_since}
                </div>
                <div className="flex items-center gap-1">
                  <Users className="w-4 h-4" />
                  {stats.followers_count} followers
                </div>
                <div className="flex items-center gap-1">
                  <Package className="w-4 h-4" />
                  {stats.products_created} products
                </div>
              </div>
            </div>
          </div>
          
          {/* Badges */}
          {badges.length > 0 && (
            <div className="mt-6 pt-6 border-t border-white/10">
              <div className="text-sm text-white/60 mb-3">Achievements</div>
              <div className="flex flex-wrap gap-2">
                {badges.map((badge, i) => (
                  <div 
                    key={i}
                    className={`px-3 py-2 rounded-lg bg-${badge.color}-500/20 border border-${badge.color}-500/30 flex items-center gap-2`}
                  >
                    <span className="text-lg">{badge.icon}</span>
                    <span className={`text-sm font-semibold text-${badge.color}-400`}>{badge.name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </motion.div>
        
        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="glass rounded-xl p-6">
            <Package className="w-8 h-8 text-cyan-400 mb-3" />
            <div className="text-3xl font-bold text-white mb-1">{stats.products_created}</div>
            <div className="text-sm text-white/60">Products Created</div>
          </div>
          
          <div className="glass rounded-xl p-6">
            <DollarSign className="w-8 h-8 text-green-400 mb-3" />
            <div className="text-3xl font-bold text-white mb-1">${stats.total_revenue?.toFixed(0)}</div>
            <div className="text-sm text-white/60">Total Revenue</div>
          </div>
          
          <div className="glass rounded-xl p-6">
            <Heart className="w-8 h-8 text-red-400 mb-3" />
            <div className="text-3xl font-bold text-white mb-1">{stats.total_likes_received}</div>
            <div className="text-sm text-white/60">Likes Received</div>
          </div>
          
          <div className="glass rounded-xl p-6">
            <TrendingUp className="w-8 h-8 text-purple-400 mb-3" />
            <div className="text-3xl font-bold text-white mb-1">{stats.engagement_rate}%</div>
            <div className="text-sm text-white/60">Engagement Rate</div>
          </div>
        </div>
        
        {/* Creator Level Progress */}
        {creatorLevel.tier && (
          <div className="glass rounded-xl p-6 mb-8">
            <h2 className="font-rajdhani text-2xl font-bold mb-4">🏆 Creator Level</h2>
            <div className="flex items-center gap-6">
              <div className="text-5xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
                {creatorLevel.level}
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <div className="text-sm text-white/60">Progress</div>
                  <div className="text-sm font-semibold">
                    {creatorLevel.points} / {creatorLevel.next_level_points || '∞'} points
                  </div>
                </div>
                <div className="w-full h-3 rounded-full bg-white/10 overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-cyan-500 to-purple-500 transition-all"
                    style={{ 
                      width: `${creatorLevel.next_level_points ? 
                        (creatorLevel.points / creatorLevel.next_level_points * 100) : 100}%` 
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Portfolio */}
        {portfolio.featured_products && portfolio.featured_products.length > 0 && (
          <div className="glass rounded-xl p-6 mb-8">
            <h2 className="font-rajdhani text-2xl font-bold mb-4">🎨 Featured Products</h2>
            <div className="grid md:grid-cols-3 gap-4">
              {portfolio.featured_products.map((product) => (
                <div key={product.id} className="p-4 rounded-lg bg-white/5 border border-white/10 hover:border-cyan-500/50 transition group">
                  {product.image_url && (
                    <img 
                      src={product.image_url} 
                      alt={product.title}
                      className="w-full h-32 object-cover rounded-lg mb-3"
                    />
                  )}
                  <h3 className="font-semibold mb-1 group-hover:text-cyan-400 transition">{product.title}</h3>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-green-400 font-bold">${product.price}</span>
                    <span className="text-white/50">{product.sales} sales</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Insights */}
        <div className="glass rounded-xl p-6">
          <h2 className="font-rajdhani text-2xl font-bold mb-4">💡 Insights</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <div className="text-sm text-white/60 mb-1">Most Popular Category</div>
              <div className="font-semibold text-cyan-400">{insights.most_popular_category}</div>
            </div>
            <div>
              <div className="text-sm text-white/60 mb-1">Average Rating</div>
              <div className="font-semibold text-yellow-400 flex items-center gap-1">
                <Star className="w-4 h-4 fill-current" />
                {insights.average_rating}
              </div>
            </div>
            <div>
              <div className="text-sm text-white/60 mb-1">Customer Satisfaction</div>
              <div className="font-semibold text-green-400">{insights.customer_satisfaction}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
