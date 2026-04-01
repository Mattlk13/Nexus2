import React, { createContext, useContext, useState, useEffect, useRef } from "react";
import { BrowserRouter, Routes, Route, Link, useNavigate, useLocation, useSearchParams, useParams } from "react-router-dom";
import { QueryClient, QueryClientProvider, useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { Toaster, toast } from "sonner";
import axios from "axios";
import {
  Music, Video, BookOpen, ShoppingCart, Star, Sparkles, Users, TrendingUp,
  Search, Menu, X, ChevronRight, Play, Heart, Share2, MessageCircle,
  Zap, Bot, DollarSign, Package, Award, Eye, Clock, ArrowRight,
  Palette, FileText, Mic, Upload, Download, Shield, Send, Plus, LogOut, User,
  Rocket, Crown, CheckCircle, Loader2, Settings, BarChart3, MessageSquare,
  Home, Grid3X3, Image, ShoppingBag, Edit, Trash2, AlertCircle, ArrowLeft, Bell, Globe, Code
} from "lucide-react";
import { NotificationBell, VendorAnalyticsPage } from "./pages/VendorPages";
import { BACKEND_URL, API } from "./config";

// Re-export for backward compatibility
export { BACKEND_URL, API };

const queryClient = new QueryClient();

// Auth Context
const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider");
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("nexus_token"));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      }).then(res => {
        setUser(res.data);
      }).catch(() => {
        localStorage.removeItem("nexus_token");
        setToken(null);
      }).finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (email, password) => {
    const res = await axios.post(`${API}/auth/login`, { email, password });
    localStorage.setItem("nexus_token", res.data.token);
    setToken(res.data.token);
    setUser(res.data.user);
    return res.data;
  };

  const register = async (email, password, username) => {
    const res = await axios.post(`${API}/auth/register`, { email, password, username });
    localStorage.setItem("nexus_token", res.data.token);
    setToken(res.data.token);
    setUser(res.data.user);
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem("nexus_token");
    setToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
    if (token) {
      const res = await axios.get(`${API}/auth/me`, { headers: { Authorization: `Bearer ${token}` }});
      setUser(res.data);
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

// API helper
export const api = {
  get: (url) => axios.get(`${API}${url}`).then(r => r.data),
  post: (url, data, token) => axios.post(`${API}${url}`, data, {
    headers: token ? { Authorization: `Bearer ${token}` } : {}
  }).then(r => r.data),
  put: (url, data, token) => axios.put(`${API}${url}`, data, {
    headers: { Authorization: `Bearer ${token}` }
  }).then(r => r.data),
  delete: (url, token) => axios.delete(`${API}${url}`, {
    headers: { Authorization: `Bearer ${token}` }
  }).then(r => r.data),
};

// ==================== COMPONENTS ====================

const Navbar = () => {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const navLinks = [
    { path: "/", label: "Home", icon: Home },
    { path: "/creation-studio", label: "Creation Studio", icon: Music },
    { path: "/marketplace", label: "Marketplace", icon: ShoppingBag },
    { path: "/feed", label: "Feed", icon: Users },
    { path: "/spotlight", label: "Spotlight", icon: Star },
    { path: "/discovery-hub", label: "Discovery", icon: TrendingUp },
    { path: "/agents", label: "AI Agents", icon: Bot },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-heavy">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2" data-testid="nav-logo">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-purple-600 flex items-center justify-center">
              <Zap className="w-5 h-5 text-black" />
            </div>
            <span className="font-rajdhani font-bold text-xl tracking-tight">NEXUS</span>
          </Link>

          <div className="hidden md:flex items-center gap-1">
            {navLinks.map(link => (
              <Link
                key={link.path}
                to={link.path}
                data-testid={`nav-${link.label.toLowerCase()}`}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  location.pathname === link.path
                    ? "bg-white/10 text-white"
                    : "text-white/60 hover:text-white hover:bg-white/5"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          <div className="hidden md:flex items-center gap-3">
            {user ? (
              <div className="flex items-center gap-3">
                <NotificationBell />
                {user.role === "admin" && (
                  <Link to="/admin" className="px-3 py-2 rounded-md bg-purple-500/20 text-purple-400 text-sm font-medium" data-testid="nav-admin">
                    Admin
                  </Link>
                )}
                {user.role === "admin" && (
                  <Link to="/admin/autonomous-engine" className="px-3 py-2 rounded-md bg-cyan-500/20 text-cyan-400 text-sm font-medium flex items-center gap-2">
                    <Bot className="w-4 h-4" />
                    Autonomous
                  </Link>
                )}
                <Link to="/vendor" className="btn-secondary px-4 py-2 rounded-md text-sm" data-testid="nav-vendor">
                  Open Shop
                </Link>
                <Link to={`/profile/${user.id}`} className="flex items-center gap-2 px-3 py-2 rounded-md bg-white/5 hover:bg-white/10 transition-colors">
                  <img src={user.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.username}`} alt="" className="w-6 h-6 rounded-full" />
                  <span className="text-sm">{user.username}</span>
                </Link>
                <button onClick={logout} className="p-2 text-white/60 hover:text-white" data-testid="nav-logout">
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <>
                <Link to="/login" className="btn-secondary px-4 py-2 rounded-md text-sm" data-testid="nav-login">
                  Sign In
                </Link>
                <Link to="/register" className="btn-primary px-4 py-2 rounded-md text-sm" data-testid="nav-register">
                  Get Started
                </Link>
              </>
            )}
          </div>

          <button className="md:hidden p-2 rounded-md hover:bg-white/10" onClick={() => setIsOpen(!isOpen)} data-testid="nav-mobile-toggle">
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden glass border-t border-white/10"
          >
            <div className="px-4 py-4 space-y-2">
              {navLinks.map(link => (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setIsOpen(false)}
                  className="flex items-center gap-3 px-4 py-3 rounded-md text-white/80 hover:bg-white/5"
                >
                  <link.icon className="w-5 h-5 text-cyan-400" />
                  {link.label}
                </Link>
              ))}
              <div className="pt-4 border-t border-white/10 space-y-2">
                {user ? (
                  <>
                    <Link to={`/profile/${user.id}`} onClick={() => setIsOpen(false)} className="block w-full btn-secondary px-4 py-3 rounded-md text-center">
                      My Profile
                    </Link>
                    <button onClick={() => { logout(); setIsOpen(false); }} className="w-full btn-secondary px-4 py-3 rounded-md">
                      Sign Out
                    </button>
                  </>
                ) : (
                  <>
                    <Link to="/login" onClick={() => setIsOpen(false)} className="block w-full btn-secondary px-4 py-3 rounded-md text-center">
                      Sign In
                    </Link>
                    <Link to="/register" onClick={() => setIsOpen(false)} className="block w-full btn-primary px-4 py-3 rounded-md text-center">
                      Get Started
                    </Link>
                  </>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

const MarqueeBar = () => {
  const items = [
    "AI Music Generation — Create full songs in seconds",
    "AI Video Studio — Generate & edit videos with AI",
    "eBook Publisher — Write & sell your books instantly",
    "Dropship Marketplace — 50,000+ products auto-listed",
    "Daily Spotlight — Get featured to 100K+ users",
    "Earn on Every Sale — Automated profit deposits",
    "5 AI Agents — Running your store 24/7",
  ];

  return (
    <div className="fixed top-16 left-0 right-0 z-40 bg-gradient-to-r from-cyan-500/10 via-purple-500/10 to-cyan-500/10 border-b border-white/5 overflow-hidden">
      <div className="flex animate-marquee whitespace-nowrap py-2">
        {[...items, ...items].map((item, i) => (
          <span key={i} className="mx-8 text-sm text-white/60 flex items-center gap-2">
            <Sparkles className="w-3 h-3 text-cyan-400" />
            {item}
          </span>
        ))}
      </div>
    </div>
  );
};

// AI Chat Support Widget
const AIChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hi! I'm NEXUS AI Assistant. How can I help you today?" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const res = await axios.post(`${API}/ai/chat`, { message: userMessage });
      setMessages(prev => [...prev, { role: "assistant", content: res.data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", content: "Sorry, I encountered an error. Please try again." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Chat Button - positioned above Emergent badge */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-24 right-6 z-[9999] w-14 h-14 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center shadow-lg hover:scale-110 transition-transform"
        data-testid="chat-widget-btn"
        style={{ zIndex: 9999 }}
      >
        <MessageSquare className="w-6 h-6 text-white" />
      </button>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-24 right-6 z-50 w-96 max-w-[calc(100vw-3rem)] glass rounded-2xl overflow-hidden shadow-2xl"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-white/10 bg-gradient-to-r from-cyan-500/10 to-purple-500/10">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold">NEXUS AI Support</h3>
                  <p className="text-xs text-green-400">Online</p>
                </div>
              </div>
              <button onClick={() => setIsOpen(false)} className="p-2 hover:bg-white/10 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Messages */}
            <div className="h-80 overflow-y-auto p-4 space-y-4">
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[80%] p-3 rounded-xl ${
                    msg.role === "user" 
                      ? "bg-cyan-500/20 text-white" 
                      : "bg-white/5 text-white/90"
                  }`}>
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-white/5 p-3 rounded-xl">
                    <Loader2 className="w-5 h-5 animate-spin text-cyan-400" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-white/10">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && sendMessage()}
                  placeholder="Ask anything..."
                  className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:border-cyan-500/50 focus:outline-none text-white placeholder:text-white/30"
                  data-testid="chat-input"
                />
                <button
                  onClick={sendMessage}
                  disabled={loading || !input.trim()}
                  className="p-2 bg-cyan-500 rounded-lg disabled:opacity-50"
                  data-testid="chat-send"
                >
                  <Send className="w-5 h-5 text-black" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

// ==================== BOOST MODAL ====================

export const BoostModal = ({ product, onClose }) => {
  const { token } = useAuth();
  const [selectedPackage, setSelectedPackage] = useState("standard");
  const [loading, setLoading] = useState(false);

  const { data: packages } = useQuery({
    queryKey: ["boost-packages"],
    queryFn: () => api.get("/boost/packages"),
  });

  const handleBoost = async () => {
    if (!token) {
      toast.error("Please sign in to boost your product");
      return;
    }

    setLoading(true);
    try {
      const originUrl = window.location.origin;
      const res = await axios.post(`${API}/boost/checkout`, {
        product_id: product.id,
        package_id: selectedPackage,
        origin_url: originUrl
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      window.location.href = res.data.checkout_url;
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to create checkout");
      setLoading(false);
    }
  };

  const packageIcons = { basic: Zap, standard: Rocket, premium: Crown };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="glass rounded-2xl p-6 max-w-lg w-full"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="font-rajdhani text-2xl font-bold">Boost Your Product</h2>
            <p className="text-sm text-white/60">Get featured in Daily Spotlight</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg" data-testid="boost-modal-close">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex items-center gap-4 p-4 rounded-xl bg-white/5 mb-6">
          <img src={product.image_url || "https://images.unsplash.com/photo-1614149162883-504ce4d13909?w=100"} alt={product.title} className="w-16 h-16 rounded-lg object-cover" />
          <div>
            <h3 className="font-semibold">{product.title}</h3>
            <p className="text-sm text-white/50">${product.price}</p>
          </div>
        </div>

        <div className="space-y-3 mb-6">
          {(packages || []).map((pkg) => {
            const Icon = packageIcons[pkg.id] || Zap;
            return (
              <button
                key={pkg.id}
                onClick={() => setSelectedPackage(pkg.id)}
                className={`w-full p-4 rounded-xl border transition-all text-left ${
                  selectedPackage === pkg.id ? "border-cyan-500 bg-cyan-500/10" : "border-white/10 hover:border-white/20"
                }`}
                data-testid={`boost-package-${pkg.id}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${selectedPackage === pkg.id ? "bg-cyan-500/20" : "bg-white/5"}`}>
                      <Icon className={`w-5 h-5 ${selectedPackage === pkg.id ? "text-cyan-400" : "text-white/60"}`} />
                    </div>
                    <div>
                      <h4 className="font-semibold">{pkg.name}</h4>
                      <p className="text-sm text-white/50">{pkg.description}</p>
                    </div>
                  </div>
                  <div className="font-rajdhani text-xl font-bold gradient-text">${pkg.price.toFixed(2)}</div>
                </div>
              </button>
            );
          })}
        </div>

        <div className="p-4 rounded-xl bg-gradient-to-r from-cyan-500/10 to-purple-500/10 mb-6">
          <h4 className="font-semibold mb-2 flex items-center gap-2">
            <Star className="w-4 h-4 text-yellow-400" /> Boost Benefits
          </h4>
          <ul className="text-sm text-white/70 space-y-1">
            <li>• Featured in Daily Spotlight section</li>
            <li>• Priority placement in search results</li>
            <li>• Highlighted with "Featured" badge</li>
            <li>• 3-5x more visibility and sales</li>
          </ul>
        </div>

        <button onClick={handleBoost} disabled={loading} className="w-full btn-primary py-4 rounded-xl flex items-center justify-center gap-2 disabled:opacity-50" data-testid="boost-checkout-btn">
          {loading ? <><Loader2 className="w-5 h-5 animate-spin" /> Processing...</> : <><Rocket className="w-5 h-5" /> Boost for ${(packages?.find(p => p.id === selectedPackage)?.price || 7.5).toFixed(2)}</>}
        </button>
      </motion.div>
    </motion.div>
  );
};

// ==================== PURCHASE MODAL ====================

export const PurchaseModal = ({ product, onClose }) => {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handlePurchase = async () => {
    if (!user) {
      toast.error("Please sign in to purchase");
      navigate("/login");
      return;
    }

    setLoading(true);
    try {
      const originUrl = window.location.origin;
      const res = await axios.post(`${API}/products/${product.id}/purchase`, {
        product_id: product.id,
        origin_url: originUrl
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      window.location.href = res.data.checkout_url;
    } catch (err) {
      toast.error(err.response?.data?.detail || "Purchase failed");
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="glass rounded-2xl p-6 max-w-md w-full"
        onClick={e => e.stopPropagation()}
      >
        <button onClick={onClose} className="absolute top-4 right-4 p-2 hover:bg-white/10 rounded-lg">
          <X className="w-5 h-5" />
        </button>

        <div className="text-center mb-6">
          <img src={product.image_url || "https://images.unsplash.com/photo-1614149162883-504ce4d13909?w=200"} alt={product.title} className="w-32 h-32 rounded-xl object-cover mx-auto mb-4" />
          <h2 className="font-rajdhani text-2xl font-bold">{product.title}</h2>
          <p className="text-white/60">by {product.vendor_name}</p>
        </div>

        <div className="p-4 rounded-xl bg-white/5 mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-white/60">Price</span>
            <span className="font-rajdhani text-2xl font-bold gradient-text">${product.price}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-white/50">
            <Shield className="w-4 h-4" />
            <span>Secure checkout with Stripe</span>
          </div>
        </div>

        <button onClick={handlePurchase} disabled={loading} className="w-full btn-primary py-4 rounded-xl flex items-center justify-center gap-2 disabled:opacity-50" data-testid="purchase-btn">
          {loading ? <><Loader2 className="w-5 h-5 animate-spin" /> Processing...</> : <><ShoppingBag className="w-5 h-5" /> Buy Now</>}
        </button>
      </motion.div>
    </motion.div>
  );
};

// ==================== HOME PAGE ====================

const HomePage = () => {
  const { data: stats } = useQuery({ queryKey: ["stats"], queryFn: () => api.get("/stats") });
  const { data: trending } = useQuery({ queryKey: ["trending"], queryFn: () => api.get("/trending") });

  const features = [
    { title: "AI Music Studio", desc: "Generate full songs, beats, and mashups with AI", icon: Music, path: "/studio" },
    { title: "Video Creator", desc: "AI video generation and professional editing tools", icon: Video, path: "/studio" },
    { title: "Writing Workshop", desc: "Blogs, stories, eBooks, and educational content", icon: FileText, path: "/studio" },
    { title: "eBook Publisher", desc: "Generate, publish, and sell eBooks instantly", icon: BookOpen, path: "/studio" },
    { title: "Dropship Market", desc: "50,000+ products auto-listed and fulfilled", icon: Package, path: "/marketplace" },
    { title: "Vendor Portal", desc: "Open your storefront and sell your creations", icon: ShoppingCart, path: "/vendor" },
    { title: "Daily Spotlight", desc: "Get featured and reach thousands of new fans", icon: Star, path: "/spotlight" },
    { title: "Social Feed", desc: "Share, discover, and connect with creators", icon: Users, path: "/feed" },
  ];

  return (
    <div className="min-h-screen pt-24">
      {/* Hero Section */}
      <section className="relative px-4 sm:px-6 py-20 md:py-32 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/5 via-transparent to-purple-500/5" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-cyan-500/10 rounded-full blur-3xl" />
        
        <div className="max-w-7xl mx-auto relative">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center">
            <div className="live-indicator inline-flex mb-6">Live Now</div>
            
            <h1 className="font-rajdhani hero-text mb-6">
              <span className="text-white">The World's First</span><br />
              <span className="gradient-text">AI Social Marketplace</span>
            </h1>
            
            <p className="text-lg md:text-xl text-white/60 max-w-3xl mx-auto mb-10">
              Create music, videos, eBooks, and more with AI. Sell to millions. Connect with creators.
              Run entirely by AI agents — <span className="text-cyan-400 font-semibold">zero manual work required.</span>
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/studio" className="btn-primary px-8 py-4 rounded-md text-lg flex items-center justify-center gap-2" data-testid="hero-create-btn">
                <Sparkles className="w-5 h-5" /> Start Creating Free
              </Link>
              <Link to="/marketplace" className="btn-secondary px-8 py-4 rounded-md text-lg flex items-center justify-center gap-2" data-testid="hero-browse-btn">
                Browse Marketplace <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </motion.div>

          {/* Stats */}
          <motion.div initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-20">
            {[
              { value: stats?.products_listed?.toLocaleString() || "50K+", label: "Products Listed" },
              { value: stats?.ai_agents_active || "11", label: "AI Agents Active" },
              { value: "∞", label: "Creator Tools" },
              { value: "24/7", label: "Fully Automated" },
            ].map((stat, i) => (
              <div key={i} className="glass rounded-xl p-6 text-center card-hover">
                <div className="font-rajdhani text-3xl md:text-4xl font-bold gradient-text mb-1">{stat.value}</div>
                <div className="text-sm text-white/50">{stat.label}</div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-4 sm:px-6 py-20 md:py-32">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-cyan-400 font-semibold mb-2">Everything You Need</p>
            <h2 className="font-rajdhani text-4xl md:text-5xl font-bold mb-4">
              One Platform. <span className="gradient-text">Infinite Possibilities.</span>
            </h2>
            <p className="text-white/60 max-w-2xl mx-auto">
              Create, sell, discover, and connect — all powered by AI and running autonomously 24/7.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {features.map((feature, i) => (
              <motion.div key={i} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.05 }}>
                <Link to={feature.path} className="block h-full glass rounded-xl p-6 card-hover group" data-testid={`feature-${feature.title.toLowerCase().replace(/\s/g, '-')}`}>
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-cyan-500/20 to-purple-500/20 flex items-center justify-center mb-4 group-hover:neon-glow transition-all">
                    <feature.icon className="w-6 h-6 text-cyan-400" />
                  </div>
                  <h3 className="font-rajdhani text-lg font-semibold mb-2">{feature.title}</h3>
                  <p className="text-sm text-white/50">{feature.desc}</p>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Trending Section */}
      <section className="px-4 sm:px-6 py-20 md:py-32 bg-gradient-to-b from-transparent via-purple-500/5 to-transparent">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-10">
            <div>
              <p className="text-cyan-400 font-semibold mb-2">Trending Now</p>
              <h2 className="font-rajdhani text-3xl md:text-4xl font-bold">Hot Content Today</h2>
            </div>
            <Link to="/marketplace" className="btn-secondary px-4 py-2 rounded-md text-sm hidden md:flex items-center gap-2">
              View All <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {(trending || []).slice(0, 4).map((item, i) => (
              <motion.div key={item.id} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }} className="glass rounded-xl overflow-hidden card-hover group">
                <div className="relative aspect-square">
                  <img src={item.image_url} alt={item.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                  <div className="absolute top-3 left-3">
                    <span className="px-2 py-1 rounded-md bg-black/60 backdrop-blur-sm text-xs font-medium capitalize">{item.category}</span>
                  </div>
                  <div className="absolute top-3 right-3">
                    <span className="px-2 py-1 rounded-md bg-cyan-500/20 text-cyan-400 text-xs font-bold">${item.price}</span>
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="font-semibold mb-1 truncate">{item.title}</h3>
                  <p className="text-sm text-white/50 mb-3">by {item.vendor_name}</p>
                  <div className="flex items-center gap-4 text-sm text-white/40">
                    <span className="flex items-center gap-1"><Heart className="w-4 h-4" /> {item.likes?.toLocaleString() || 0}</span>
                    <span className="flex items-center gap-1"><Eye className="w-4 h-4" /> {item.views?.toLocaleString() || 0}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* AI Agents Section - Updated to 11 agents */}
      <section className="px-4 sm:px-6 py-20 md:py-32">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-cyan-400 font-semibold mb-2">AI Workforce</p>
            <h2 className="font-rajdhani text-4xl md:text-5xl font-bold mb-4">
              46 AI Agents. <span className="gradient-text">Running Everything.</span>
            </h2>
            <p className="text-white/60 max-w-2xl mx-auto">
              From operations to marketing to AI tool discovery — fully autonomous with Manus AI orchestration.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { name: "CEO Agent", time: "8PM Daily", task: "Reviews KPIs, sends profit reports", icon: TrendingUp, type: "Core" },
              { name: "Product Manager", time: "6AM Daily", task: "Imports trending products, optimizes catalog", icon: Package, type: "Core" },
              { name: "Marketing Agent", time: "12PM Daily", task: "Posts to social platforms, creates campaigns", icon: Share2, type: "Core" },
              { name: "Vendor Manager", time: "9AM Daily", task: "Approves vendors, moderates listings", icon: Users, type: "Core" },
              { name: "Finance Agent", time: "8:30PM Daily", task: "Tracks revenue, processes payouts", icon: DollarSign, type: "Core" },
              { name: "Tool Discovery", time: "3AM Daily", task: "Searches GitHub/GitLab for beneficial tools", icon: Sparkles, type: "Manus" },
              { name: "Investor Outreach", time: "10AM Daily", task: "Finds VCs, creates pitch materials", icon: Rocket, type: "Manus" },
              { name: "Marketing Automation", time: "2PM Daily", task: "Auto-generates marketing campaigns", icon: BarChart3, type: "Manus" },
              { name: "Platform Optimizer", time: "11PM Daily", task: "Analyzes metrics, suggests improvements", icon: Settings, type: "Manus" },
              { name: "CI/CD Monitor", time: "4AM Daily", task: "Monitors deployments, runs health checks", icon: Zap, type: "Manus" },
              { name: "AIxploria Discovery", time: "2AM Daily", task: "Scans AIxploria, GitHub, ProductHunt, Softr for AI tools", icon: Globe, type: "Autonomous" },
            ].map((agent, i) => (
              <motion.div 
                key={i} 
                initial={{ opacity: 0, x: -20 }} 
                whileInView={{ opacity: 1, x: 0 }} 
                viewport={{ once: true }} 
                transition={{ delay: i * 0.05 }} 
                className="glass rounded-xl p-6 flex items-start gap-4 card-hover"
              >
                <div className={`w-12 h-12 rounded-lg ${
                  agent.type === "Core" ? "bg-green-500/10 border border-green-500/30" : 
                  agent.type === "Manus" ? "bg-purple-500/10 border border-purple-500/30" :
                  "bg-cyan-500/10 border border-cyan-500/30"
                } flex items-center justify-center flex-shrink-0`}>
                  <agent.icon className={`w-6 h-6 ${
                    agent.type === "Core" ? "text-green-400" : 
                    agent.type === "Manus" ? "text-purple-400" :
                    "text-cyan-400"
                  }`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="status-active status-pulse" />
                    <span className={`text-xs font-semibold uppercase ${
                      agent.type === "Core" ? "text-green-400" : 
                      agent.type === "Manus" ? "text-purple-400" :
                      "text-cyan-400"
                    }`}>{agent.type}</span>
                  </div>
                  <h3 className="font-rajdhani text-lg font-semibold">{agent.name}</h3>
                  <p className="text-xs text-white/40 mb-2">{agent.time}</p>
                  <p className="text-sm text-white/60">{agent.task}</p>
                </div>
              </motion.div>
            ))}
          </div>
          
          <div className="text-center mt-12">
            <Link to="/agents" className="btn-secondary px-6 py-3 rounded-md inline-flex items-center gap-2">
              View Agent Dashboard <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-4 sm:px-6 py-20 md:py-32">
        <div className="max-w-4xl mx-auto">
          <div className="gradient-border rounded-2xl p-8 md:p-16 text-center">
            <h2 className="font-rajdhani text-4xl md:text-5xl font-bold mb-4">
              Ready to Build Your <span className="gradient-text">Autonomous Empire?</span>
            </h2>
            <p className="text-white/60 mb-8 max-w-2xl mx-auto">
              Join NEXUS today. Create, sell, and earn — while AI handles everything else.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/register" className="btn-primary px-8 py-4 rounded-md text-lg">Join Free — No Credit Card</Link>
              <Link to="/vendor" className="btn-secondary px-8 py-4 rounded-md text-lg">Open Your Store</Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-4 sm:px-6 py-10 border-t border-white/10">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-purple-600 flex items-center justify-center">
              <Zap className="w-5 h-5 text-black" />
            </div>
            <span className="font-rajdhani font-bold text-xl">NEXUS</span>
          </div>
          <p className="text-sm text-white/40">© 2025 NEXUS. AI-Powered Social Marketplace.</p>
        </div>
      </footer>
    </div>
  );
};

// Import pages
import { MarketplacePage, ProductDetailPage, ProfilePage, PurchaseSuccessPage, MyPurchasesPage } from "./pages/MarketplacePages";
import { StudioPage, FeedPage, SpotlightPage, AgentsPage, VendorPage, BoostSuccessPage } from "./pages/CorePages";
import { AdminDashboard, LoginPage, RegisterPage } from "./pages/AdminPages";
import { InvestorDashboardPage } from "./pages/InvestorPages";
import { EnhancedProfilePage } from "./pages/EnhancedProfilePage";
import { APIPlaygroundPage } from "./pages/APIPlaygroundPage";
import { AdminAnalyticsPage } from "./pages/AdminAnalyticsPage";
import { GitHubConnectionPage } from "./pages/GitHubConnectionPage";
import { DiscoveryHubPage } from "./pages/DiscoveryHubPage";
import { CloudflareConfigPage } from "./pages/CloudflareConfigPage";
import { AutonomousEnginePage } from "./pages/AutonomousEnginePage";
import MessengerPage from "./pages/MessengerPage";
import AutonomousSystemsDashboard from "./pages/AutonomousSystemsDashboard";
import Newsfeed from "./pages/Newsfeed";
import CreationStudio from "./pages/CreationStudio";
import MessengerPopup from "./components/MessengerPopup";
import SocialAutomationDashboard from "./pages/SocialAutomationDashboard";
import CreatedContentPage from "./pages/CreatedContentPage";
import IconShowcase from "./pages/IconShowcase";
import HybridShowcase from "./pages/HybridShowcase";
import NetNeutralityDashboard from "./pages/NetNeutralityDashboard";
import MLStudio from "./pages/MLStudio";
import MusicStudio from "./pages/MusicStudio";
import InvestorDashboard from "./pages/InvestorDashboard";
import DevToolsHub from "./pages/DevToolsHub";
import OpenSourceHub from "./pages/OpenSourceHub";
import AIModelsHub from "./pages/AIModelsHub";
import WebGamesHub from "./pages/WebGamesHub";
import AccessibilityHub from "./pages/AccessibilityHub";
import JSStateHub from "./pages/JSStateHub";
import PHPQualityHub from "./pages/PHPQualityHub";
import AllHybridsShowcase from "./pages/AllHybridsShowcase";
import OmmaHub from "./pages/OmmaHub";
import SocialNetwork from "./pages/SocialNetwork";
import Marketplace from "./pages/Marketplace";
import Messages from "./pages/Messages";
import Profile from "./pages/Profile";
import AdminDashboardNew from "./pages/AdminDashboard";
import AgentStudio from "./pages/AgentStudio";

// ==================== MAIN APP ====================

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <div className="App min-h-screen bg-[#050505]">
          <div className="noise-overlay" />
          <BrowserRouter>
            <Navbar />
            <MarqueeBar />
            <Routes>
              <Route path="/" element={<Newsfeed />} />
              <Route path="/home" element={<HomePage />} />
              <Route path="/creation-studio" element={<CreationStudio />} />
              <Route path="/created-content" element={<CreatedContentPage />} />
              <Route path="/social-automation" element={<SocialAutomationDashboard />} />
              <Route path="/marketplace" element={<MarketplacePage />} />
              <Route path="/products/:productId" element={<ProductDetailPage />} />
              <Route path="/studio" element={<StudioPage />} />
              <Route path="/feed" element={<FeedPage />} />
              <Route path="/spotlight" element={<SpotlightPage />} />
              <Route path="/agents" element={<AgentsPage />} />
              <Route path="/vendor" element={<VendorPage />} />
              <Route path="/vendor/analytics" element={<VendorAnalyticsPage />} />
              <Route path="/profile/:userId" element={<ProfilePage />} />
              <Route path="/profile/:userId/enhanced" element={<EnhancedProfilePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/boost/success" element={<BoostSuccessPage />} />
              <Route path="/purchase/success" element={<PurchaseSuccessPage />} />
              <Route path="/my-purchases" element={<MyPurchasesPage />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/admin/investors" element={<InvestorDashboardPage />} />
              <Route path="/admin/analytics" element={<AdminAnalyticsPage />} />
              <Route path="/admin/autonomous-engine" element={<AutonomousEnginePage />} />
              <Route path="/admin/autonomous-systems" element={<AutonomousSystemsDashboard />} />
              <Route path="/settings/github" element={<GitHubConnectionPage />} />
              <Route path="/settings/cloudflare" element={<CloudflareConfigPage />} />
              <Route path="/discovery-hub" element={<DiscoveryHubPage />} />
              <Route path="/api-playground" element={<APIPlaygroundPage />} />
              <Route path="/messenger" element={<MessengerPage />} />
              <Route path="/icons" element={<IconShowcase />} />
              <Route path="/hybrids" element={<HybridShowcase />} />
              <Route path="/net-neutrality" element={<NetNeutralityDashboard />} />
              <Route path="/ml-studio" element={<MLStudio />} />
              <Route path="/music-studio" element={<MusicStudio />} />
              <Route path="/investor-dashboard" element={<InvestorDashboard />} />
              <Route path="/dev-tools" element={<DevToolsHub />} />
              <Route path="/opensource" element={<OpenSourceHub />} />
              <Route path="/ai-models" element={<AIModelsHub />} />
              <Route path="/web-games" element={<WebGamesHub />} />
              <Route path="/accessibility" element={<AccessibilityHub />} />
              <Route path="/js-state" element={<JSStateHub />} />
              <Route path="/php-quality" element={<PHPQualityHub />} />
              <Route path="/all-hybrids" element={<AllHybridsShowcase />} />
              <Route path="/omma" element={<OmmaHub />} />
              <Route path="/social" element={<SocialNetwork />} />
              <Route path="/studio" element={<CreationStudio />} />
              <Route path="/marketplace" element={<Marketplace />} />
              <Route path="/messages" element={<Messages />} />
              <Route path="/profile-new" element={<Profile />} />
              <Route path="/admin-dashboard" element={<AdminDashboardNew />} />
              <Route path="/agent-studio" element={<AgentStudio />} />
            </Routes>
            <MessengerPopup />
            <AIChatWidget />
          </BrowserRouter>
          <Toaster position="top-center" richColors />
        </div>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
