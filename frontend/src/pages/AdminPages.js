import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { toast } from "sonner";
import axios from "axios";
import {
  Users, TrendingUp, DollarSign, Package, Eye, Trash2, Settings, BarChart3,
  Bot, Zap, ShoppingCart, FileText, Loader2, AlertCircle, CheckCircle,
  User, Crown, Shield, Sparkles, Rocket, ChevronRight
} from "lucide-react";
import { useAuth, api, API } from "../App";
import { AutomationPanel } from "../components/AutomationPanel";

// ==================== ADMIN DASHBOARD ====================

export const AdminDashboard = () => {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState("overview");

  const { data: dashboard, isLoading } = useQuery({
    queryKey: ["admin-dashboard"],
    queryFn: () => axios.get(`${API}/admin/dashboard`, { headers: { Authorization: `Bearer ${token}` }}).then(r => r.data),
    enabled: user?.role === "admin",
  });

  const { data: users } = useQuery({
    queryKey: ["admin-users"],
    queryFn: () => axios.get(`${API}/admin/users`, { headers: { Authorization: `Bearer ${token}` }}).then(r => r.data),
    enabled: user?.role === "admin" && activeTab === "users",
  });

  const { data: products } = useQuery({
    queryKey: ["admin-products"],
    queryFn: () => axios.get(`${API}/admin/products`, { headers: { Authorization: `Bearer ${token}` }}).then(r => r.data),
    enabled: user?.role === "admin" && activeTab === "products",
  });

  const deleteUser = useMutation({
    mutationFn: (userId) => axios.delete(`${API}/admin/users/${userId}`, { headers: { Authorization: `Bearer ${token}` }}),
    onSuccess: () => { queryClient.invalidateQueries(["admin-users"]); toast.success("User deleted"); },
  });

  const deleteProduct = useMutation({
    mutationFn: (productId) => axios.delete(`${API}/admin/products/${productId}`, { headers: { Authorization: `Bearer ${token}` }}),
    onSuccess: () => { queryClient.invalidateQueries(["admin-products"]); toast.success("Product deleted"); },
  });

  const updateRole = useMutation({
    mutationFn: ({ userId, role }) => axios.put(`${API}/admin/users/${userId}/role?role=${role}`, {}, { headers: { Authorization: `Bearer ${token}` }}),
    onSuccess: () => { queryClient.invalidateQueries(["admin-users"]); toast.success("Role updated"); },
  });

  const runAgent = async (agentId) => {
    try {
      toast.loading("Running agent...");
      await axios.post(`${API}/agents/${agentId}/run`, {}, { headers: { Authorization: `Bearer ${token}` }});
      toast.dismiss();
      toast.success("Agent completed!");
      queryClient.invalidateQueries(["admin-dashboard"]);
    } catch (err) { toast.dismiss(); toast.error("Failed"); }
  };

  if (!user || user.role !== "admin") {
    return (
      <div className="min-h-screen pt-28 flex items-center justify-center">
        <div className="glass rounded-xl p-8 text-center">
          <Shield className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="font-rajdhani text-2xl font-bold mb-2">Admin Access Required</h2>
          <p className="text-white/60 mb-6">You don't have permission to access this page.</p>
          <Link to="/" className="btn-primary px-6 py-3 rounded-md">Go Home</Link>
        </div>
      </div>
    );
  }

  if (isLoading) return <div className="min-h-screen pt-28 flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-cyan-400" /></div>;

  const stats = dashboard?.stats || {};

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-rajdhani text-4xl font-bold"><span className="gradient-text">Admin Dashboard</span></h1>
            <p className="text-white/60">Manage your platform</p>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-purple-500/20 border border-purple-500/30">
            <Crown className="w-5 h-5 text-purple-400" />
            <span className="text-purple-400 font-semibold">Admin</span>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-8 overflow-x-auto">
          {["overview", "users", "products", "agents", "automation", "investors", "reports"].map((tab) => (
            <button key={tab} onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 rounded-lg whitespace-nowrap transition-all capitalize ${activeTab === tab ? "bg-cyan-500 text-black font-semibold" : "bg-white/5 text-white/60 hover:bg-white/10"}`}>
              {tab}
            </button>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === "overview" && (
          <>
            {/* Cloudflare Integration Link */}
            <Link to="/settings/cloudflare"
              className="glass rounded-xl p-6 mb-6 flex items-center justify-between group hover:bg-white/10 transition-all">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center">
                  <Zap className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-rajdhani text-xl font-bold mb-1">⚡ Cloudflare Integration</h3>
                  <p className="text-white/60 text-sm">Configure KV, R2, Workers AI, Vectorize & more</p>
                </div>
              </div>
              <ChevronRight className="w-6 h-6 text-orange-400 group-hover:translate-x-2 transition-transform" />
            </Link>

            {/* Analytics Dashboard Link */}
            <Link to="/admin/analytics"
              className="glass rounded-xl p-6 mb-6 flex items-center justify-between group hover:bg-white/10 transition-all">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center">
                  <BarChart3 className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-rajdhani text-xl font-bold mb-1">📊 Advanced Analytics Dashboard</h3>
                  <p className="text-white/60 text-sm">View comprehensive insights, revenue trends, and user growth charts</p>
                </div>
              </div>
              <ChevronRight className="w-6 h-6 text-cyan-400 group-hover:translate-x-2 transition-transform" />
            </Link>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              {[
                { label: "Total Users", value: stats.users, icon: Users, color: "cyan" },
                { label: "Products", value: stats.products, icon: Package, color: "purple" },
                { label: "Vendors", value: stats.vendors, icon: ShoppingCart, color: "green" },
                { label: "Total Revenue", value: `$${(stats.total_revenue || 0).toFixed(2)}`, icon: DollarSign, color: "yellow" },
              ].map((stat, i) => (
                <div key={i} className="glass rounded-xl p-6">
                  <div className="flex items-center gap-3 mb-2">
                    <stat.icon className={`w-6 h-6 text-${stat.color}-400`} />
                    <span className="text-white/50 text-sm">{stat.label}</span>
                  </div>
                  <div className="font-rajdhani text-3xl font-bold">{stat.value}</div>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Revenue Breakdown */}
              <div className="glass rounded-xl p-6">
                <h3 className="font-rajdhani text-xl font-bold mb-4">Revenue Breakdown</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-white/60">Boost Revenue</span>
                    <span className="font-semibold text-cyan-400">${(stats.boost_revenue || 0).toFixed(2)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-white/60">Sales Revenue</span>
                    <span className="font-semibold text-green-400">${(stats.sales_revenue || 0).toFixed(2)}</span>
                  </div>
                  <div className="flex items-center justify-between pt-4 border-t border-white/10">
                    <span className="font-semibold">Total</span>
                    <span className="font-rajdhani text-2xl font-bold gradient-text">${(stats.total_revenue || 0).toFixed(2)}</span>
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="glass rounded-xl p-6">
                <h3 className="font-rajdhani text-xl font-bold mb-4">Recent Users</h3>
                <div className="space-y-3">
                  {(dashboard?.recent_users || []).slice(0, 5).map((u) => (
                    <div key={u.id} className="flex items-center gap-3 p-2 rounded-lg bg-white/5">
                      <img src={u.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${u.username}`} alt="" className="w-8 h-8 rounded-full" />
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold truncate">{u.username}</p>
                        <p className="text-xs text-white/50">{u.email}</p>
                      </div>
                      <span className={`px-2 py-1 rounded text-xs ${u.role === "admin" ? "bg-purple-500/20 text-purple-400" : u.role === "vendor" ? "bg-cyan-500/20 text-cyan-400" : "bg-white/10 text-white/60"}`}>
                        {u.role}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Agent Reports */}
            <div className="glass rounded-xl p-6 mt-6">
              <h3 className="font-rajdhani text-xl font-bold mb-4">Latest Agent Reports</h3>
              <div className="space-y-4">
                {(dashboard?.agent_reports || []).map((report) => (
                  <div key={report.id} className="p-4 rounded-lg bg-white/5">
                    <div className="flex items-center gap-2 mb-2">
                      <Bot className="w-4 h-4 text-green-400" />
                      <span className="font-semibold capitalize">{report.agent} Agent</span>
                      <span className="text-xs text-white/40">{new Date(report.created_at).toLocaleString()}</span>
                    </div>
                    <p className="text-sm text-white/70 line-clamp-3">{report.content}</p>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Users Tab */}
        {activeTab === "users" && (
          <div className="glass rounded-xl overflow-hidden">
            <div className="p-4 border-b border-white/10">
              <h3 className="font-semibold">All Users ({users?.total || 0})</h3>
            </div>
            <div className="divide-y divide-white/10">
              {(users?.users || []).map((u) => (
                <div key={u.id} className="p-4 flex items-center gap-4">
                  <img src={u.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${u.username}`} alt="" className="w-10 h-10 rounded-full" />
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold">{u.username}</p>
                    <p className="text-sm text-white/50">{u.email}</p>
                  </div>
                  <select value={u.role} onChange={(e) => updateRole.mutate({ userId: u.id, role: e.target.value })}
                    className="px-3 py-1 rounded-lg bg-white/5 border border-white/10 text-sm">
                    <option value="user">User</option>
                    <option value="vendor">Vendor</option>
                    <option value="admin">Admin</option>
                  </select>
                  <button onClick={() => deleteUser.mutate(u.id)} className="p-2 text-red-400 hover:bg-red-500/10 rounded-lg">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Products Tab */}
        {activeTab === "products" && (
          <div className="glass rounded-xl overflow-hidden">
            <div className="p-4 border-b border-white/10">
              <h3 className="font-semibold">All Products ({products?.total || 0})</h3>
            </div>
            <div className="divide-y divide-white/10">
              {(products?.products || []).map((p) => (
                <div key={p.id} className="p-4 flex items-center gap-4">
                  <img src={p.image_url || "https://images.unsplash.com/photo-1614149162883-504ce4d13909?w=100"} alt="" className="w-12 h-12 rounded-lg object-cover" />
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold">{p.title}</p>
                    <p className="text-sm text-white/50">by {p.vendor_name} • ${p.price}</p>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-white/50">
                    <span><Eye className="w-4 h-4 inline mr-1" />{p.views}</span>
                    <span><DollarSign className="w-4 h-4 inline mr-1" />{p.sales || 0}</span>
                  </div>
                  <button onClick={() => deleteProduct.mutate(p.id)} className="p-2 text-red-400 hover:bg-red-500/10 rounded-lg">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Agents Tab */}
        {activeTab === "agents" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {["ceo", "product_manager", "marketing", "vendor_manager", "finance"].map((agentId) => (
              <div key={agentId} className="glass rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                      <Bot className="w-5 h-5 text-green-400" />
                    </div>
                    <div>
                      <h4 className="font-semibold capitalize">{agentId.replace("_", " ")} Agent</h4>
                      <p className="text-xs text-green-400">Active</p>
                    </div>
                  </div>
                  <button onClick={() => runAgent(agentId)} className="btn-primary px-4 py-2 rounded-md text-sm">
                    Run Now
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Reports Tab */}
        {activeTab === "reports" && (
          <div className="space-y-4">
            {(dashboard?.agent_reports || []).map((report) => (
              <div key={report.id} className="glass rounded-xl p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Bot className="w-5 h-5 text-green-400" />
                  <span className="font-rajdhani text-lg font-bold capitalize">{report.agent} Agent Report</span>
                  <span className="text-sm text-white/40 ml-auto">{new Date(report.created_at).toLocaleString()}</span>
                </div>
                <div className="prose prose-invert max-w-none">
                  <pre className="text-sm text-white/80 whitespace-pre-wrap bg-black/40 p-4 rounded-lg">{report.content}</pre>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Automation Tab */}
        {activeTab === "automation" && (
          <AutomationPanel token={token} />
        )}
        
        {/* Investors Tab */}
        {activeTab === "investors" && (
          <div className="space-y-6">
            <div className="glass rounded-xl p-6">
              <h2 className="font-rajdhani text-2xl font-bold mb-4">🚀 Investor Resources</h2>
              <p className="text-white/70 mb-6">
                Access comprehensive investor dashboard with platform metrics, growth analytics, and curated investor database.
              </p>
              <Link 
                to="/admin/investors"
                className="btn-primary px-6 py-3 rounded-lg inline-flex items-center gap-2"
              >
                <Rocket className="w-5 h-5" />
                Open Investor Dashboard
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ==================== AUTH PAGES ====================

export const LoginPage = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      toast.success("Welcome back!");
      navigate("/");
    } catch (err) { toast.error(err.response?.data?.detail || "Login failed"); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6 flex items-center justify-center">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="font-rajdhani text-3xl font-bold mb-2">Welcome Back</h1>
          <p className="text-white/60">Sign in to your NEXUS account</p>
        </div>

        <form onSubmit={handleSubmit} className="glass rounded-xl p-6 md:p-8 space-y-6">
          <div>
            <label className="block text-sm font-medium text-white/60 mb-2">Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-cyan-500/50 focus:outline-none text-white placeholder:text-white/30" data-testid="login-email" />
          </div>
          <div>
            <label className="block text-sm font-medium text-white/60 mb-2">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" required
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-cyan-500/50 focus:outline-none text-white placeholder:text-white/30" data-testid="login-password" />
          </div>
          <button type="submit" disabled={loading} className="w-full btn-primary py-4 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50" data-testid="login-submit">
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Sign In"}
          </button>
          <p className="text-center text-white/50 text-sm">
            Don't have an account? <Link to="/register" className="text-cyan-400 hover:underline">Sign up</Link>
          </p>
        </form>
      </div>
    </div>
  );
};

export const RegisterPage = () => {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register(email, password, username);
      toast.success("Account created!");
      navigate("/");
    } catch (err) { toast.error(err.response?.data?.detail || "Registration failed"); }
    finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6 flex items-center justify-center">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="font-rajdhani text-3xl font-bold mb-2">Join NEXUS</h1>
          <p className="text-white/60">Create your free account</p>
        </div>

        <form onSubmit={handleSubmit} className="glass rounded-xl p-6 md:p-8 space-y-6">
          <div>
            <label className="block text-sm font-medium text-white/60 mb-2">Username</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Choose a username" required
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-cyan-500/50 focus:outline-none text-white placeholder:text-white/30" data-testid="register-username" />
          </div>
          <div>
            <label className="block text-sm font-medium text-white/60 mb-2">Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-cyan-500/50 focus:outline-none text-white placeholder:text-white/30" data-testid="register-email" />
          </div>
          <div>
            <label className="block text-sm font-medium text-white/60 mb-2">Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" required minLength={6}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-cyan-500/50 focus:outline-none text-white placeholder:text-white/30" data-testid="register-password" />
          </div>
          <button type="submit" disabled={loading} className="w-full btn-primary py-4 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50" data-testid="register-submit">
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Create Account"}
          </button>
          <p className="text-center text-white/50 text-sm">
            Already have an account? <Link to="/login" className="text-cyan-400 hover:underline">Sign in</Link>
          </p>
        </form>
      </div>
    </div>
  );
};

export default { AdminDashboard, LoginPage, RegisterPage };
