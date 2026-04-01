import React, { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import axios from "axios";
import { io } from "socket.io-client";
import {
  Bell, TrendingUp, DollarSign, Package, Eye, Heart, BarChart3, 
  ShoppingBag, Clock, ArrowUp, ArrowDown, Loader2, CheckCircle,
  X, ChevronRight, Users, Zap
} from "lucide-react";
import { useAuth, API } from "../App";
import { BACKEND_URL } from "../config";

// ==================== WEBSOCKET HOOK ====================

export const useSocket = () => {
  const { token } = useAuth();
  const socketRef = useRef(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!token) return;

    socketRef.current = io(BACKEND_URL, {
      path: "/api/socket.io",
      transports: ["websocket", "polling"]
    });

    socketRef.current.on("connect", () => {
      console.log("Socket connected");
      setConnected(true);
      // Authenticate
      socketRef.current.emit("authenticate", { token });
    });

    socketRef.current.on("disconnect", () => {
      console.log("Socket disconnected");
      setConnected(false);
    });

    socketRef.current.on("authenticated", (data) => {
      if (data.success) {
        console.log("Socket authenticated");
      }
    });

    return () => {
      if (socketRef.current?.connected) {
        socketRef.current.disconnect();
      }
    };
  }, [token]);

  return { socket: socketRef.current, connected };
};

// ==================== NOTIFICATIONS COMPONENT ====================

export const NotificationBell = () => {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  const [isOpen, setIsOpen] = useState(false);
  const { socket } = useSocket();

  const { data: notifications, refetch } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => axios.get(`${API}/notifications`, { headers: { Authorization: `Bearer ${token}` }}).then(r => r.data),
    enabled: !!token,
    refetchInterval: 30000
  });

  // Listen for real-time notifications
  useEffect(() => {
    if (!socket) return;
    
    socket.on("notification", (notification) => {
      queryClient.setQueryData(["notifications"], (old) => {
        return old ? [notification, ...old] : [notification];
      });
      toast(notification.title, { description: notification.message });
    });

    return () => {
      socket.off("notification");
    };
  }, [socket, queryClient]);

  const unreadCount = (notifications || []).filter(n => !n.read).length;

  const markAllRead = async () => {
    try {
      await axios.put(`${API}/notifications/read-all`, {}, { headers: { Authorization: `Bearer ${token}` }});
      refetch();
    } catch (err) {
      console.error(err);
    }
  };

  const notificationIcons = {
    sale: ShoppingBag,
    like: Heart,
    comment: Users,
    follow: Users,
    agent_report: Zap
  };

  if (!token) return null;

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-lg hover:bg-white/10 transition-colors"
        data-testid="notification-bell"
      >
        <Bell className="w-5 h-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            className="absolute right-0 top-12 w-80 glass rounded-xl overflow-hidden shadow-2xl z-50"
          >
            <div className="flex items-center justify-between p-4 border-b border-white/10">
              <h3 className="font-semibold">Notifications</h3>
              {unreadCount > 0 && (
                <button onClick={markAllRead} className="text-xs text-cyan-400 hover:underline">
                  Mark all read
                </button>
              )}
            </div>

            <div className="max-h-96 overflow-y-auto">
              {(notifications || []).length === 0 ? (
                <div className="p-8 text-center text-white/50">
                  <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>No notifications yet</p>
                </div>
              ) : (
                (notifications || []).slice(0, 10).map((notif) => {
                  const Icon = notificationIcons[notif.type] || Bell;
                  return (
                    <div
                      key={notif.id}
                      className={`p-4 border-b border-white/5 hover:bg-white/5 transition-colors ${!notif.read ? "bg-cyan-500/5" : ""}`}
                    >
                      <div className="flex gap-3">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${!notif.read ? "bg-cyan-500/20" : "bg-white/10"}`}>
                          <Icon className={`w-5 h-5 ${!notif.read ? "text-cyan-400" : "text-white/50"}`} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-semibold text-sm">{notif.title}</p>
                          <p className="text-sm text-white/60 truncate">{notif.message}</p>
                          <p className="text-xs text-white/40 mt-1">
                            {new Date(notif.created_at).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// ==================== VENDOR ANALYTICS PAGE ====================

export const VendorAnalyticsPage = () => {
  const { user, token } = useAuth();
  const navigate = useNavigate();

  const { data: analytics, isLoading } = useQuery({
    queryKey: ["vendor-analytics"],
    queryFn: () => axios.get(`${API}/vendor/analytics`, { headers: { Authorization: `Bearer ${token}` }}).then(r => r.data),
    enabled: !!token
  });

  const { data: products } = useQuery({
    queryKey: ["vendor-products"],
    queryFn: () => axios.get(`${API}/vendor/products`, { headers: { Authorization: `Bearer ${token}` }}).then(r => r.data),
    enabled: !!token
  });

  if (!user) {
    return (
      <div className="min-h-screen pt-28 flex items-center justify-center">
        <div className="glass rounded-xl p-8 text-center">
          <BarChart3 className="w-16 h-16 text-cyan-400 mx-auto mb-4" />
          <h2 className="font-rajdhani text-2xl font-bold mb-2">Vendor Analytics</h2>
          <p className="text-white/60 mb-6">Sign in to view your analytics</p>
          <Link to="/login" className="btn-primary px-6 py-3 rounded-md inline-block">Sign In</Link>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen pt-28 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
      </div>
    );
  }

  const overview = analytics?.overview || {};

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-rajdhani text-4xl font-bold"><span className="gradient-text">Vendor Analytics</span></h1>
            <p className="text-white/60">Track your sales and performance</p>
          </div>
          <Link to="/vendor" className="btn-secondary px-4 py-2 rounded-md">
            Manage Shop
          </Link>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          {[
            { label: "Products", value: overview.total_products || 0, icon: Package, color: "cyan" },
            { label: "Views", value: overview.total_views?.toLocaleString() || 0, icon: Eye, color: "blue" },
            { label: "Likes", value: overview.total_likes?.toLocaleString() || 0, icon: Heart, color: "pink" },
            { label: "Sales", value: overview.total_sales || 0, icon: ShoppingBag, color: "green" },
            { label: "Revenue", value: `$${(overview.total_revenue || 0).toFixed(2)}`, icon: DollarSign, color: "yellow" },
            { label: "Conversion", value: `${overview.conversion_rate || 0}%`, icon: TrendingUp, color: "purple" },
          ].map((stat, i) => (
            <div key={i} className="glass rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <stat.icon className={`w-5 h-5 text-${stat.color}-400`} />
                <span className="text-sm text-white/50">{stat.label}</span>
              </div>
              <div className="font-rajdhani text-2xl font-bold">{stat.value}</div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Products */}
          <div className="glass rounded-xl p-6">
            <h3 className="font-rajdhani text-xl font-bold mb-4">Top Products</h3>
            <div className="space-y-3">
              {(analytics?.top_products || []).map((product, i) => (
                <div key={product.id} className="flex items-center gap-4 p-3 rounded-lg bg-white/5">
                  <span className="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 text-sm flex items-center justify-center font-bold">
                    {i + 1}
                  </span>
                  <img src={product.image_url || "https://images.unsplash.com/photo-1614149162883-504ce4d13909?w=100"} alt="" className="w-10 h-10 rounded-lg object-cover" />
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold truncate">{product.title}</p>
                    <p className="text-sm text-white/50">${product.price}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-green-400">{product.sales || 0} sales</p>
                    <p className="text-xs text-white/40">{product.views || 0} views</p>
                  </div>
                </div>
              ))}
              {(!analytics?.top_products || analytics.top_products.length === 0) && (
                <p className="text-center text-white/50 py-4">No products yet</p>
              )}
            </div>
          </div>

          {/* Recent Sales */}
          <div className="glass rounded-xl p-6">
            <h3 className="font-rajdhani text-xl font-bold mb-4">Recent Sales</h3>
            <div className="space-y-3">
              {(analytics?.recent_sales || []).map((sale) => (
                <div key={sale.id} className="flex items-center gap-4 p-3 rounded-lg bg-white/5">
                  <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center">
                    <DollarSign className="w-5 h-5 text-green-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold">${(sale.amount * 0.85).toFixed(2)}</p>
                    <p className="text-sm text-white/50">{new Date(sale.created_at).toLocaleDateString()}</p>
                  </div>
                  <span className="px-2 py-1 rounded-md bg-green-500/20 text-green-400 text-xs">
                    Completed
                  </span>
                </div>
              ))}
              {(!analytics?.recent_sales || analytics.recent_sales.length === 0) && (
                <p className="text-center text-white/50 py-4">No sales yet</p>
              )}
            </div>
          </div>
        </div>

        {/* Products List */}
        <div className="glass rounded-xl p-6 mt-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-rajdhani text-xl font-bold">Your Products</h3>
            <Link to="/studio" className="text-cyan-400 text-sm hover:underline">
              Create New
            </Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-white/50 text-sm border-b border-white/10">
                  <th className="pb-3 font-medium">Product</th>
                  <th className="pb-3 font-medium">Price</th>
                  <th className="pb-3 font-medium">Views</th>
                  <th className="pb-3 font-medium">Likes</th>
                  <th className="pb-3 font-medium">Sales</th>
                  <th className="pb-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {(products || []).map((product) => (
                  <tr key={product.id} className="border-b border-white/5">
                    <td className="py-3">
                      <div className="flex items-center gap-3">
                        <img src={product.image_url || "https://images.unsplash.com/photo-1614149162883-504ce4d13909?w=100"} alt="" className="w-10 h-10 rounded-lg object-cover" />
                        <Link to={`/products/${product.id}`} className="font-semibold hover:text-cyan-400 truncate max-w-[200px]">
                          {product.title}
                        </Link>
                      </div>
                    </td>
                    <td className="py-3">${product.price}</td>
                    <td className="py-3">{product.views || 0}</td>
                    <td className="py-3">{product.likes || 0}</td>
                    <td className="py-3 text-green-400">{product.sales || 0}</td>
                    <td className="py-3">
                      {product.is_boosted ? (
                        <span className="px-2 py-1 rounded-md bg-cyan-500/20 text-cyan-400 text-xs">Boosted</span>
                      ) : (
                        <span className="px-2 py-1 rounded-md bg-white/10 text-white/50 text-xs">Active</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {(!products || products.length === 0) && (
              <div className="text-center py-8">
                <Package className="w-12 h-12 text-white/20 mx-auto mb-2" />
                <p className="text-white/50">No products yet. Create your first product!</p>
                <Link to="/studio" className="btn-primary px-4 py-2 rounded-md inline-block mt-4">
                  Create Product
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default { useSocket, NotificationBell, VendorAnalyticsPage };
