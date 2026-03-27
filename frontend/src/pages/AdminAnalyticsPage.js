import React from "react";
import { useQuery } from "@tanstack/react-query";
import axios from "axios";
import { motion } from "framer-motion";
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from "recharts";
import {
  TrendingUp, Users, DollarSign, Package, Activity,
  Award, ShoppingCart, Loader2
} from "lucide-react";
import { useAuth, API } from "../App";

const COLORS = ['#06b6d4', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6'];

export const AdminAnalyticsPage = () => {
  const { token } = useAuth();

  const { data: analytics, isLoading } = useQuery({
    queryKey: ["admin-analytics-comprehensive"],
    queryFn: () => axios.get(`${API}/admin/analytics/comprehensive`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.data),
    refetchInterval: 60000 // Refresh every minute
  });

  if (isLoading) {
    return (
      <div className="min-h-screen pt-28 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
      </div>
    );
  }

  const overview = analytics?.overview || {};
  const revenue = analytics?.revenue || {};
  const userGrowth = analytics?.user_growth || {};
  const topProducts = analytics?.top_products || [];
  const topVendors = analytics?.top_vendors || [];
  const categoryDist = analytics?.category_distribution || {};
  const engagement = analytics?.engagement || {};

  // Format currency
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(value);
  };

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="font-rajdhani text-4xl font-bold mb-2">
            <span className="gradient-text">Analytics Dashboard</span>
          </h1>
          <p className="text-white/60">Comprehensive platform insights and metrics</p>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          <StatCard
            icon={DollarSign}
            label="Total Revenue"
            value={formatCurrency(overview.total_revenue || 0)}
            color="cyan"
          />
          <StatCard
            icon={Users}
            label="Total Users"
            value={overview.total_users?.toLocaleString() || '0'}
            color="purple"
          />
          <StatCard
            icon={Award}
            label="Total Vendors"
            value={overview.total_vendors?.toLocaleString() || '0'}
            color="pink"
          />
          <StatCard
            icon={Package}
            label="Total Products"
            value={overview.total_products?.toLocaleString() || '0'}
            color="blue"
          />
          <StatCard
            icon={ShoppingCart}
            label="Total Orders"
            value={overview.total_orders?.toLocaleString() || '0'}
            color="green"
          />
        </div>

        {/* Revenue Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-xl p-6 mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="font-rajdhani text-2xl font-bold mb-1">Revenue Trend</h2>
              <p className="text-white/60 text-sm">Last 12 months</p>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-500/20 border border-cyan-500/30">
              <TrendingUp className="w-4 h-4 text-cyan-400" />
              <span className="text-cyan-400 font-semibold">{revenue.growth_rate || '+0%'}</span>
            </div>
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={revenue.chart_data || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="month" stroke="rgba(255,255,255,0.5)" />
              <YAxis stroke="rgba(255,255,255,0.5)" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(0,0,0,0.8)',
                  border: '1px solid rgba(6,182,212,0.3)',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#06b6d4"
                strokeWidth={2}
                dot={{ fill: '#06b6d4', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* User Growth Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass rounded-xl p-6 mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="font-rajdhani text-2xl font-bold mb-1">User Growth</h2>
              <p className="text-white/60 text-sm">New users and cumulative total</p>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-500/20 border border-purple-500/30">
              <Users className="w-4 h-4 text-purple-400" />
              <span className="text-purple-400 font-semibold">{userGrowth.growth_rate || '+0%'}</span>
            </div>
          </div>
          
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={userGrowth.chart_data || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="month" stroke="rgba(255,255,255,0.5)" />
              <YAxis stroke="rgba(255,255,255,0.5)" />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'rgba(0,0,0,0.8)',
                  border: '1px solid rgba(139,92,246,0.3)',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Bar dataKey="new_users" fill="#8b5cf6" name="New Users" />
              <Bar dataKey="total_users" fill="#06b6d4" name="Total Users" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Top Products */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="glass rounded-xl p-6"
          >
            <h2 className="font-rajdhani text-2xl font-bold mb-4">Top Products</h2>
            <div className="space-y-3">
              {topProducts.slice(0, 5).map((product, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center font-bold text-sm">
                      #{idx + 1}
                    </div>
                    <div>
                      <p className="font-medium">{product.title || 'Unknown'}</p>
                      <p className="text-xs text-white/50">{product.sales || 0} sales</p>
                    </div>
                  </div>
                  <span className="text-cyan-400 font-semibold">
                    {formatCurrency(product.price * product.sales || 0)}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Top Vendors */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="glass rounded-xl p-6"
          >
            <h2 className="font-rajdhani text-2xl font-bold mb-4">Top Vendors</h2>
            <div className="space-y-3">
              {topVendors.slice(0, 5).map((vendor, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center font-bold text-sm">
                      #{idx + 1}
                    </div>
                    <div>
                      <p className="font-medium">{vendor.vendor_name || 'Unknown'}</p>
                      <p className="text-xs text-white/50">{vendor.products_count || 0} products</p>
                    </div>
                  </div>
                  <span className="text-purple-400 font-semibold">
                    {formatCurrency(vendor.total_revenue || 0)}
                  </span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Category Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass rounded-xl p-6 mb-8"
        >
          <h2 className="font-rajdhani text-2xl font-bold mb-6">Category Distribution</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={categoryDist.categories?.slice(0, 6) || []}
                  dataKey="revenue"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label
                >
                  {(categoryDist.categories || []).slice(0, 6).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    border: '1px solid rgba(6,182,212,0.3)',
                    borderRadius: '8px'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>

            <div className="space-y-3">
              {(categoryDist.categories || []).slice(0, 6).map((cat, idx) => (
                <div key={idx} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                    />
                    <span className="text-sm">{cat.name}</span>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-sm">{formatCurrency(cat.revenue)}</p>
                    <p className="text-xs text-white/50">{cat.products} products</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Engagement Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass rounded-xl p-6"
        >
          <h2 className="font-rajdhani text-2xl font-bold mb-6">Engagement Metrics</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-lg bg-white/5">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="w-5 h-5 text-cyan-400" />
                <span className="text-sm text-white/60">Posts (30d)</span>
              </div>
              <p className="text-2xl font-bold">{engagement.posts_last_30d?.toLocaleString() || '0'}</p>
            </div>

            <div className="p-4 rounded-lg bg-white/5">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-5 h-5 text-purple-400" />
                <span className="text-sm text-white/60">Total Likes</span>
              </div>
              <p className="text-2xl font-bold">{engagement.total_likes?.toLocaleString() || '0'}</p>
            </div>

            <div className="p-4 rounded-lg bg-white/5">
              <div className="flex items-center gap-2 mb-2">
                <Users className="w-5 h-5 text-pink-400" />
                <span className="text-sm text-white/60">Total Views</span>
              </div>
              <p className="text-2xl font-bold">{engagement.total_views?.toLocaleString() || '0'}</p>
            </div>

            <div className="p-4 rounded-lg bg-white/5">
              <div className="flex items-center gap-2 mb-2">
                <Award className="w-5 h-5 text-green-400" />
                <span className="text-sm text-white/60">Engagement Rate</span>
              </div>
              <p className="text-2xl font-bold">{engagement.engagement_rate || '0%'}</p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

// Stat Card Component
const StatCard = ({ icon: Icon, label, value, color }) => {
  const colorClasses = {
    cyan: 'from-cyan-500 to-cyan-600',
    purple: 'from-purple-500 to-purple-600',
    pink: 'from-pink-500 to-pink-600',
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600'
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass rounded-xl p-4"
    >
      <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${colorClasses[color]} flex items-center justify-center mb-3`}>
        <Icon className="w-5 h-5 text-white" />
      </div>
      <p className="text-white/60 text-sm mb-1">{label}</p>
      <p className="text-2xl font-bold">{value}</p>
    </motion.div>
  );
};
