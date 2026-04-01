import React, { useState, useEffect } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import axios from "axios";
import {
  Music, Video, BookOpen, ShoppingCart, Star, Sparkles, Users, TrendingUp,
  Search, X, Heart, Share2, MessageCircle, Zap, Bot, DollarSign, Package, 
  Award, Eye, Clock, ArrowRight, Palette, FileText, Upload, Download, Send, 
  Plus, User, Rocket, Crown, CheckCircle, Loader2, Settings, BarChart3,
  Edit, Trash2, ArrowLeft, Image as ImageIcon, ShoppingBag
} from "lucide-react";
import { useAuth, api, BoostModal, PurchaseModal } from "../App";
import { BACKEND_URL, API } from "../config";
import { AuctionBiddingWidget } from "../components/AuctionBiddingWidget";

// ==================== MARKETPLACE PAGE ====================

export const MarketplacePage = () => {
  const { user, token } = useAuth();
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [boostProduct, setBoostProduct] = useState(null);
  const [purchaseProduct, setPurchaseProduct] = useState(null);
  
  const { data: products, isLoading } = useQuery({
    queryKey: ["products", category, search],
    queryFn: () => api.get(`/products?category=${category}&search=${search}`),
  });
  
  const { data: categories } = useQuery({
    queryKey: ["categories"],
    queryFn: () => api.get("/categories"),
  });

  const categoryIcons = { music: Music, video: Video, ebook: BookOpen, art: Palette, templates: FileText, dropship: Package, services: Zap, courses: Award };

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-10">
          <h1 className="font-rajdhani text-4xl md:text-5xl font-bold mb-4"><span className="gradient-text">Marketplace</span></h1>
          <p className="text-white/60">Discover AI-generated content, digital products, and more</p>
        </div>

        <div className="glass rounded-xl p-4 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
              <input type="text" placeholder="Search products..." value={search} onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-cyan-500/50 focus:outline-none text-white placeholder:text-white/30" data-testid="marketplace-search" />
            </div>
            <div className="flex gap-2 overflow-x-auto hide-scrollbar">
              <button onClick={() => setCategory("all")} className={`px-4 py-2 rounded-lg whitespace-nowrap transition-all ${category === "all" ? "bg-cyan-500 text-black font-semibold" : "bg-white/5 text-white/60 hover:bg-white/10"}`} data-testid="category-all">All</button>
              {(categories || []).map((cat) => {
                const Icon = categoryIcons[cat.id] || Package;
                return (
                  <button key={cat.id} onClick={() => setCategory(cat.id)} className={`px-4 py-2 rounded-lg flex items-center gap-2 whitespace-nowrap transition-all ${category === cat.id ? "bg-cyan-500 text-black font-semibold" : "bg-white/5 text-white/60 hover:bg-white/10"}`} data-testid={`category-${cat.id}`}>
                    <Icon className="w-4 h-4" /> {cat.name}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(8)].map((_, i) => (
              <div key={i} className="glass rounded-xl overflow-hidden animate-pulse">
                <div className="aspect-square bg-white/5" />
                <div className="p-4 space-y-3"><div className="h-4 bg-white/5 rounded w-3/4" /><div className="h-3 bg-white/5 rounded w-1/2" /></div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {(products || []).map((product) => (
              <motion.div key={product.id} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="glass rounded-xl overflow-hidden card-hover group">
                <div className="relative aspect-square cursor-pointer" onClick={() => setPurchaseProduct(product)}>
                  <img src={product.image_url || `https://images.unsplash.com/photo-1614149162883-504ce4d13909?w=400`} alt={product.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                  {product.is_ai_generated && (
                    <div className="absolute top-3 left-3"><span className="px-2 py-1 rounded-md bg-purple-500/20 border border-purple-500/30 text-purple-400 text-xs font-medium flex items-center gap-1"><Sparkles className="w-3 h-3" /> AI</span></div>
                  )}
                  {product.is_boosted && (
                    <div className="absolute top-3 left-3"><span className="px-2 py-1 rounded-md bg-yellow-500/20 border border-yellow-500/30 text-yellow-400 text-xs font-medium flex items-center gap-1"><Star className="w-3 h-3" /> Featured</span></div>
                  )}
                  <div className="absolute top-3 right-3"><span className="px-3 py-1 rounded-md bg-cyan-500/20 text-cyan-400 text-sm font-bold">${product.price}</span></div>
                </div>
                <div className="p-4">
                  <Link to={`/products/${product.id}`}><h3 className="font-semibold mb-1 truncate hover:text-cyan-400">{product.title}</h3></Link>
                  <Link to={`/profile/${product.vendor_id}`} className="text-sm text-white/50 mb-3 block hover:text-white/70">by {product.vendor_name}</Link>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 text-sm text-white/40">
                      <span className="flex items-center gap-1"><Heart className="w-4 h-4" /> {product.likes || 0}</span>
                      <span className="flex items-center gap-1"><Eye className="w-4 h-4" /> {product.views || 0}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {user && product.vendor_id === user.id && !product.is_boosted && (
                        <button onClick={() => setBoostProduct(product)} className="p-2 rounded-md bg-gradient-to-r from-cyan-500/20 to-purple-500/20 hover:from-cyan-500/30 hover:to-purple-500/30 transition-colors" data-testid={`product-boost-${product.id}`} title="Boost to Spotlight">
                          <Rocket className="w-4 h-4 text-cyan-400" />
                        </button>
                      )}
                      <button onClick={() => setPurchaseProduct(product)} className="p-2 rounded-md bg-white/5 hover:bg-cyan-500/20 transition-colors" data-testid={`product-buy-${product.id}`}>
                        <ShoppingBag className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {(!products || products.length === 0) && !isLoading && (
          <div className="text-center py-20">
            <Package className="w-16 h-16 text-white/20 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No products found</h3>
            <p className="text-white/50">Try adjusting your search or filters</p>
          </div>
        )}
      </div>

      <AnimatePresence>
        {boostProduct && <BoostModal product={boostProduct} onClose={() => setBoostProduct(null)} />}
        {purchaseProduct && <PurchaseModal product={purchaseProduct} onClose={() => setPurchaseProduct(null)} />}
      </AnimatePresence>
    </div>
  );
};

// ==================== PRODUCT DETAIL PAGE ====================

export const ProductDetailPage = () => {
  const { productId } = useParams();
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [purchasing, setPurchasing] = useState(false);

  const { data: product, isLoading } = useQuery({
    queryKey: ["product", productId],
    queryFn: () => api.get(`/products/${productId}`),
  });

  const handlePurchase = async () => {
    if (!user) { toast.error("Please sign in"); navigate("/login"); return; }
    setPurchasing(true);
    try {
      const res = await axios.post(`${API}/products/${productId}/purchase`, { product_id: productId, origin_url: window.location.origin }, { headers: { Authorization: `Bearer ${token}` }});
      window.location.href = res.data.checkout_url;
    } catch (err) { toast.error(err.response?.data?.detail || "Purchase failed"); setPurchasing(false); }
  };

  if (isLoading) return <div className="min-h-screen pt-28 flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-cyan-400" /></div>;
  if (!product) return <div className="min-h-screen pt-28 flex items-center justify-center"><p>Product not found</p></div>;

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-white/60 hover:text-white mb-6"><ArrowLeft className="w-5 h-5" /> Back</button>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="glass rounded-2xl overflow-hidden">
            <img src={product.image_url || "https://images.unsplash.com/photo-1614149162883-504ce4d13909?w=600"} alt={product.title} className="w-full aspect-square object-cover" />
          </div>
          
          <div>
            <div className="flex items-center gap-2 mb-4">
              {product.is_ai_generated && <span className="px-3 py-1 rounded-full bg-purple-500/20 text-purple-400 text-sm flex items-center gap-1"><Sparkles className="w-4 h-4" /> AI Generated</span>}
              <span className="px-3 py-1 rounded-full bg-white/10 text-sm capitalize">{product.category}</span>
            </div>
            
            <h1 className="font-rajdhani text-4xl font-bold mb-4">{product.title}</h1>
            
            <Link to={`/profile/${product.vendor_id}`} className="flex items-center gap-3 mb-6 p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors">
              <img src={product.vendor?.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${product.vendor_name}`} alt="" className="w-10 h-10 rounded-full" />
              <div>
                <p className="font-semibold">{product.vendor_name}</p>
                <p className="text-sm text-white/50">View profile</p>
              </div>
            </Link>
            
            <p className="text-white/70 mb-6">{product.description}</p>
            
            <div className="flex items-center gap-6 mb-6 text-white/60">
              <span className="flex items-center gap-2"><Heart className="w-5 h-5" /> {product.likes} likes</span>
              <span className="flex items-center gap-2"><Eye className="w-5 h-5" /> {product.views} views</span>
              <span className="flex items-center gap-2"><ShoppingBag className="w-5 h-5" /> {product.sales || 0} sales</span>
            </div>
            
            <div className="glass rounded-xl p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <span className="text-white/60">Price</span>
                <span className="font-rajdhani text-4xl font-bold gradient-text">${product.price}</span>
              </div>
              <button onClick={handlePurchase} disabled={purchasing} className="w-full btn-primary py-4 rounded-xl flex items-center justify-center gap-2 disabled:opacity-50" data-testid="product-purchase-btn">
                {purchasing ? <><Loader2 className="w-5 h-5 animate-spin" /> Processing...</> : <><ShoppingBag className="w-5 h-5" /> Buy Now</>}
              </button>
            </div>
            
            {/* Auction Bidding Widget */}
            {product.is_auction && <AuctionBiddingWidget product={product} />}
            
            {product.tags?.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {product.tags.map((tag, i) => <span key={i} className="px-3 py-1 rounded-full bg-white/5 text-sm">#{tag}</span>)}
              </div>
            )}
          </div>
        </div>
        
        {product.related_products?.length > 0 && (
          <div className="mt-16">
            <h2 className="font-rajdhani text-2xl font-bold mb-6">Related Products</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {product.related_products.map((p) => (
                <Link key={p.id} to={`/products/${p.id}`} className="glass rounded-xl overflow-hidden card-hover">
                  <img src={p.image_url || "https://images.unsplash.com/photo-1614149162883-504ce4d13909?w=200"} alt={p.title} className="w-full aspect-square object-cover" />
                  <div className="p-3">
                    <h3 className="font-semibold text-sm truncate">{p.title}</h3>
                    <p className="text-cyan-400 font-bold">${p.price}</p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ==================== USER PROFILE PAGE ====================

export const ProfilePage = () => {
  const { userId } = useParams();
  const { user: currentUser, token } = useAuth();
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [bio, setBio] = useState("");

  const { data: profile, isLoading } = useQuery({
    queryKey: ["profile", userId],
    queryFn: () => api.get(`/users/${userId}`),
  });

  const followMutation = useMutation({
    mutationFn: () => api.post(`/users/${userId}/follow`, {}, token),
    onSuccess: () => { queryClient.invalidateQueries(["profile", userId]); toast.success("Updated!"); },
  });

  const updateMutation = useMutation({
    mutationFn: (data) => api.put("/users/profile", data, token),
    onSuccess: () => { queryClient.invalidateQueries(["profile", userId]); setEditing(false); toast.success("Profile updated!"); },
  });

  useEffect(() => { if (profile) setBio(profile.bio || ""); }, [profile]);

  if (isLoading) return <div className="min-h-screen pt-28 flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-cyan-400" /></div>;
  if (!profile) return <div className="min-h-screen pt-28 flex items-center justify-center"><p>User not found</p></div>;

  const isOwner = currentUser?.id === userId;

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="glass rounded-2xl p-8 mb-8">
          <div className="flex flex-col md:flex-row gap-6 items-start">
            <img src={profile.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${profile.username}`} alt="" className="w-24 h-24 rounded-full" />
            <div className="flex-1">
              <div className="flex items-center gap-4 mb-2">
                <h1 className="font-rajdhani text-3xl font-bold">{profile.username}</h1>
                {profile.role === "vendor" && <span className="px-2 py-1 rounded-md bg-cyan-500/20 text-cyan-400 text-xs font-semibold">Vendor</span>}
                {profile.role === "admin" && <span className="px-2 py-1 rounded-md bg-purple-500/20 text-purple-400 text-xs font-semibold">Admin</span>}
              </div>
              
              {editing ? (
                <div className="mb-4">
                  <textarea value={bio} onChange={(e) => setBio(e.target.value)} className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:border-cyan-500/50 focus:outline-none text-white" rows={3} />
                  <div className="flex gap-2 mt-2">
                    <button onClick={() => updateMutation.mutate({ bio })} className="btn-primary px-4 py-2 rounded-md text-sm">Save</button>
                    <button onClick={() => setEditing(false)} className="btn-secondary px-4 py-2 rounded-md text-sm">Cancel</button>
                  </div>
                </div>
              ) : (
                <p className="text-white/60 mb-4">{profile.bio || "No bio yet"}</p>
              )}
              
              <div className="flex items-center gap-6 text-sm">
                <span><strong>{profile.followers_count}</strong> <span className="text-white/50">followers</span></span>
                <span><strong>{profile.following_count}</strong> <span className="text-white/50">following</span></span>
                <span><strong>{profile.products?.length || 0}</strong> <span className="text-white/50">products</span></span>
              </div>
            </div>
            
            <div className="flex gap-2">
              {isOwner ? (
                <button onClick={() => setEditing(true)} className="btn-secondary px-4 py-2 rounded-md flex items-center gap-2"><Edit className="w-4 h-4" /> Edit Profile</button>
              ) : currentUser && (
                <button onClick={() => followMutation.mutate()} className="btn-primary px-6 py-2 rounded-md">
                  {followMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : "Follow"}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Products */}
        {profile.products?.length > 0 && (
          <div className="mb-8">
            <h2 className="font-rajdhani text-2xl font-bold mb-6">Products</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {profile.products.map((product) => (
                <Link key={product.id} to={`/products/${product.id}`} className="glass rounded-xl overflow-hidden card-hover">
                  <img src={product.image_url || "https://images.unsplash.com/photo-1614149162883-504ce4d13909?w=200"} alt={product.title} className="w-full aspect-square object-cover" />
                  <div className="p-3">
                    <h3 className="font-semibold text-sm truncate">{product.title}</h3>
                    <p className="text-cyan-400 font-bold">${product.price}</p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Posts */}
        {profile.posts?.length > 0 && (
          <div>
            <h2 className="font-rajdhani text-2xl font-bold mb-6">Posts</h2>
            <div className="space-y-4">
              {profile.posts.map((post) => (
                <div key={post.id} className="glass rounded-xl p-4">
                  <p className="text-white/80 mb-2">{post.content}</p>
                  <div className="flex items-center gap-4 text-sm text-white/40">
                    <span className="flex items-center gap-1"><Heart className="w-4 h-4" /> {post.likes}</span>
                    <span className="flex items-center gap-1"><MessageCircle className="w-4 h-4" /> {post.comments_count}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// ==================== PURCHASE SUCCESS PAGE ====================

export const PurchaseSuccessPage = () => {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get("session_id");
  const [status, setStatus] = useState("checking");
  const [attempts, setAttempts] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    if (!sessionId) { navigate("/marketplace"); return; }
    const poll = async () => {
      if (attempts >= 10) { setStatus("timeout"); return; }
      try {
        const res = await axios.get(`${API}/purchase/status/${sessionId}`);
        if (res.data.payment_status === "paid" || res.data.transaction_status === "completed") { setStatus("success"); }
        else if (res.data.status === "expired") { setStatus("expired"); }
        else { setTimeout(() => setAttempts(a => a + 1), 2000); }
      } catch { setTimeout(() => setAttempts(a => a + 1), 2000); }
    };
    poll();
  }, [sessionId, attempts, navigate]);

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6 flex items-center justify-center">
      <div className="max-w-md w-full">
        {status === "checking" && (
          <div className="glass rounded-2xl p-8 text-center">
            <Loader2 className="w-16 h-16 text-cyan-400 animate-spin mx-auto mb-6" />
            <h2 className="font-rajdhani text-2xl font-bold mb-2">Processing Payment</h2>
            <p className="text-white/60">Please wait...</p>
          </div>
        )}
        {status === "success" && (
          <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="glass rounded-2xl p-8 text-center">
            <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-6" />
            <h2 className="font-rajdhani text-2xl font-bold mb-2">Purchase Complete!</h2>
            <p className="text-white/60 mb-6">Your purchase has been added to your library.</p>
            <div className="space-y-3">
              <Link to="/my-purchases" className="block w-full btn-primary py-3 rounded-lg">View My Purchases</Link>
              <Link to="/marketplace" className="block w-full btn-secondary py-3 rounded-lg">Continue Shopping</Link>
            </div>
          </motion.div>
        )}
        {status === "expired" && (
          <div className="glass rounded-2xl p-8 text-center">
            <X className="w-16 h-16 text-red-400 mx-auto mb-6" />
            <h2 className="font-rajdhani text-2xl font-bold mb-2">Payment Failed</h2>
            <p className="text-white/60 mb-6">The payment session has expired.</p>
            <Link to="/marketplace" className="block w-full btn-secondary py-3 rounded-lg">Back to Marketplace</Link>
          </div>
        )}
      </div>
    </div>
  );
};

// ==================== MY PURCHASES PAGE ====================

export const MyPurchasesPage = () => {
  const { token } = useAuth();
  const { data: purchases, isLoading } = useQuery({
    queryKey: ["my-purchases"],
    queryFn: () => api.get("/my-purchases"),
    enabled: !!token,
  });

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6">
      <div className="max-w-5xl mx-auto">
        <h1 className="font-rajdhani text-4xl font-bold mb-8"><span className="gradient-text">My Purchases</span></h1>
        
        {isLoading ? (
          <div className="flex justify-center py-20"><Loader2 className="w-8 h-8 animate-spin text-cyan-400" /></div>
        ) : purchases?.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {purchases.map((purchase) => (
              <div key={purchase.id} className="glass rounded-xl overflow-hidden">
                <img src={purchase.product?.image_url || "https://images.unsplash.com/photo-1614149162883-504ce4d13909?w=300"} alt="" className="w-full aspect-video object-cover" />
                <div className="p-4">
                  <h3 className="font-semibold mb-2">{purchase.product?.title}</h3>
                  <p className="text-sm text-white/50 mb-4">Purchased {new Date(purchase.purchased_at).toLocaleDateString()}</p>
                  <button className="w-full btn-primary py-2 rounded-md flex items-center justify-center gap-2"><Download className="w-4 h-4" /> Download</button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-20">
            <ShoppingBag className="w-16 h-16 text-white/20 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No purchases yet</h3>
            <p className="text-white/50 mb-6">Start exploring the marketplace!</p>
            <Link to="/marketplace" className="btn-primary px-6 py-3 rounded-md inline-block">Browse Marketplace</Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default { MarketplacePage, ProductDetailPage, ProfilePage, PurchaseSuccessPage, MyPurchasesPage };
