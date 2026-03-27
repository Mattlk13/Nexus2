import React, { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import axios from "axios";
import {
  Music, Video, BookOpen, Star, Sparkles, Users, TrendingUp, Heart, Share2, 
  MessageCircle, Zap, Bot, DollarSign, Package, Award, Eye, Clock, 
  ArrowRight, Palette, FileText, Download, Upload, User, Rocket, 
  Crown, CheckCircle, Loader2, BarChart3, Settings, Trash2, X
} from "lucide-react";
import { useAuth, api, BoostModal, API } from "../App";

// ==================== STUDIO PAGE ====================

export const StudioPage = () => {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("music");
  const [prompt, setPrompt] = useState("");
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [showPublishModal, setShowPublishModal] = useState(false);
  const [publishData, setPublishData] = useState({ title: "", description: "", price: 9.99, tags: "" });
  
  // Video generation parameters
  const [videoProvider, setVideoProvider] = useState("sora");  // "sora" or "runway"
  const [videoParams, setVideoParams] = useState({
    model: "sora-2",
    size: "1280x720",
    duration: 4
  });
  
  // Runway-specific parameters
  const [runwayParams, setRunwayParams] = useState({
    model: "gen3a_turbo",
    duration: 5,
    aspect_ratio: "16:9"
  });

  const tabs = [
    { id: "music", label: "Music", icon: Music },
    { id: "video", label: "Text-to-Video", icon: Video },
    { id: "text", label: "Writing", icon: FileText },
    { id: "ebook", label: "eBook", icon: BookOpen },
    { id: "image", label: "Image", icon: Palette },
    { id: "voice", label: "Voice", icon: Music },
  ];

  const handleGenerate = async () => {
    if (!user) { toast.error("Please sign in"); navigate("/login"); return; }
    if (!prompt.trim()) { toast.error("Please enter a prompt"); return; }

    setGenerating(true);
    setResult(null);
    try {
      const requestData = { 
        prompt, 
        content_type: activeTab
      };
      
      // Add video parameters based on selected provider
      if (activeTab === "video") {
        requestData.video_provider = videoProvider;
        
        if (videoProvider === "runway") {
          requestData.video_params = runwayParams;
        } else {
          requestData.video_params = videoParams;
        }
      }
      
      const res = await axios.post(`${API}/ai/generate`, requestData, { headers: { Authorization: `Bearer ${token}` }});
      setResult(res.data);
      
      // If Runway, start polling for status
      if (activeTab === "video" && videoProvider === "runway" && res.data.task_id) {
        toast.success("Runway video generation started! Checking status...");
        pollRunwayStatus(res.data.task_id);
      } else {
        toast.success(activeTab === "video" ? "Video generated!" : "Content generated!");
      }
    } catch (err) { 
      toast.error(err.response?.data?.detail || "Generation failed"); 
    }
    finally { setGenerating(false); }
  };
  
  const pollRunwayStatus = async (taskId) => {
    const maxAttempts = 120; // 10 minutes with 5-second intervals
    let attempts = 0;
    
    const pollInterval = setInterval(async () => {
      try {
        const res = await axios.get(`${API}/runway/status/${taskId}`, { 
          headers: { Authorization: `Bearer ${token}` }
        });
        
        const { status, local_url, error } = res.data;
        
        if (status === "SUCCEEDED" && local_url) {
          clearInterval(pollInterval);
          setResult(prev => ({
            ...prev,
            video_url: local_url,
            status: "complete"
          }));
          toast.success("✓ Runway video ready!");
        } else if (status === "FAILED") {
          clearInterval(pollInterval);
          toast.error(`Video generation failed: ${error || "Unknown error"}`);
        }
        
        attempts++;
        if (attempts > maxAttempts) {
          clearInterval(pollInterval);
          toast.error("Video generation timeout");
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 5000);
  };
  
  const handleDownload = async () => {
    try {
      toast.loading("Preparing download...");
      const downloadRes = await axios.post(
        `${API}/studio/download`,
        {
          content_type: result.content_type,
          content: result.result,
          title: publishData.title || prompt.substring(0, 50),
          audio_url: result.audio_url,
          image_data: result.image_data
        },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      toast.dismiss();
      
      // Trigger download
      const link = document.createElement('a');
      link.href = downloadRes.data.download_url;
      link.download = downloadRes.data.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast.success(`✓ Downloaded: ${downloadRes.data.filename}`);
    } catch (err) {
      toast.dismiss();
      toast.error(err.response?.data?.detail || "Download failed");
    }
  };
  
  const handlePublish = async () => {
    try {
      if (!publishData.title) {
        toast.error("Please enter a title");
        return;
      }
      
      toast.loading("Publishing to marketplace...");
      
      const publishRes = await axios.post(
        `${API}/studio/publish-to-marketplace`,
        {
          title: publishData.title,
          description: publishData.description,
          price: publishData.price,
          category: activeTab,
          file_url: result.audio_url || result.image_data || "generated-content",
          image_url: result.image_data,
          thumbnail_url: result.image_data,
          tags: publishData.tags.split(',').map(t => t.trim()).filter(Boolean)
        },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      toast.dismiss();
      toast.success(`✓ Published to marketplace!`);
      setShowPublishModal(false);
      
      // Navigate to product
      setTimeout(() => {
        navigate(`/products/${publishRes.data.product_id}`);
      }, 1500);
      
    } catch (err) {
      toast.dismiss();
      toast.error(err.response?.data?.detail || "Publishing failed");
    }
  };

  const promptSuggestions = {
    music: ["A dreamy synthwave track with 80s vibes", "Upbeat pop song about summer adventures", "Epic orchestral music for a fantasy game"],
    video: [
      "A cat wearing sunglasses riding a skateboard through a city",
      "Cinematic drone shot of a mountain landscape at golden hour",
      "Time-lapse of flowers blooming in a garden",
      "A futuristic robot walking through neon-lit streets"
    ],
    text: ["A blog post about AI in creative industries", "A short story about time travel", "A guide to productivity hacks"],
    ebook: ["A complete guide to prompt engineering", "A sci-fi novel about AI consciousness", "A cookbook for healthy meals"],
    image: ["A futuristic cityscape at night with neon lights", "A cosmic portrait with galaxies", "Abstract art with vibrant colors"],
  };

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="font-rajdhani text-4xl md:text-5xl font-bold mb-4"><span className="gradient-text">Creator Studio</span></h1>
          <p className="text-white/60">Generate music, videos, images, and more with AI</p>
        </div>

        <div className="glass rounded-xl p-2 mb-8 flex gap-2 overflow-x-auto hide-scrollbar">
          {tabs.map((tab) => (
            <button key={tab.id} onClick={() => { setActiveTab(tab.id); setResult(null); }}
              className={`flex-1 min-w-[120px] flex items-center justify-center gap-2 px-4 py-3 rounded-lg transition-all ${activeTab === tab.id ? "bg-cyan-500 text-black font-semibold" : "text-white/60 hover:bg-white/5"}`} data-testid={`studio-tab-${tab.id}`}>
              <tab.icon className="w-5 h-5" /> {tab.label}
            </button>
          ))}
        </div>

        <div className="glass rounded-xl p-6 md:p-8">
          <div className="mb-6">
            <label className="block text-sm font-medium text-white/60 mb-2">What would you like to create?</label>
            <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder={`Describe your ${activeTab} idea...`} rows={4}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-cyan-500/50 focus:outline-none text-white placeholder:text-white/30 resize-none" data-testid="studio-prompt" />
          </div>

          {/* Video Generation Parameters */}
          {activeTab === "video" && (
            <div className="mb-6 space-y-4 p-4 bg-white/5 rounded-lg border border-white/10">
              <h3 className="text-sm font-semibold text-white/80 mb-3">🎬 Video Generation Settings</h3>
              
              {/* Provider Selection */}
              <div>
                <label className="block text-xs text-white/60 mb-2">AI Provider</label>
                <select 
                  value={videoProvider} 
                  onChange={(e) => setVideoProvider(e.target.value)}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm focus:border-cyan-500/50 focus:outline-none"
                >
                  <option value="sora">Sora 2 (OpenAI)</option>
                  <option value="runway">Runway Gen-3 (Runway ML)</option>
                </select>
              </div>
              
              {videoProvider === "runway" ? (
                /* Runway Parameters */
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs text-white/60 mb-2">Model</label>
                    <select 
                      value={runwayParams.model} 
                      onChange={(e) => setRunwayParams({...runwayParams, model: e.target.value})}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm focus:border-cyan-500/50 focus:outline-none"
                    >
                      <option value="gen3a_turbo">Gen-3 Alpha Turbo (Fast)</option>
                      <option value="gen3_alpha">Gen-3 Alpha (Quality)</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-xs text-white/60 mb-2">Resolution</label>
                    <select 
                      value={runwayParams.aspect_ratio} 
                      onChange={(e) => setRunwayParams({...runwayParams, aspect_ratio: e.target.value})}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm focus:border-cyan-500/50 focus:outline-none"
                    >
                      <option value="16:9">16:9 (Widescreen)</option>
                      <option value="9:16">9:16 (Portrait)</option>
                      <option value="1280:768">1280:768 (Wide)</option>
                      <option value="768:1280">768:1280 (Tall)</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-xs text-white/60 mb-2">Duration</label>
                    <select 
                      value={runwayParams.duration} 
                      onChange={(e) => setRunwayParams({...runwayParams, duration: parseInt(e.target.value)})}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm focus:border-cyan-500/50 focus:outline-none"
                    >
                      <option value="5">5 seconds</option>
                      <option value="10">10 seconds</option>
                    </select>
                  </div>
                </div>
              ) : (
                /* Sora 2 Parameters */
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-xs text-white/60 mb-2">Quality</label>
                    <select 
                      value={videoParams.model} 
                      onChange={(e) => setVideoParams({...videoParams, model: e.target.value})}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm focus:border-cyan-500/50 focus:outline-none"
                    >
                      <option value="sora-2">Sora 2 (Standard)</option>
                      <option value="sora-2-pro">Sora 2 Pro (High Quality)</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-xs text-white/60 mb-2">Resolution</label>
                    <select 
                      value={videoParams.size} 
                      onChange={(e) => setVideoParams({...videoParams, size: e.target.value})}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm focus:border-cyan-500/50 focus:outline-none"
                    >
                      <option value="1280x720">1280x720 (HD)</option>
                      <option value="1792x1024">1792x1024 (Widescreen)</option>
                      <option value="1024x1792">1024x1792 (Portrait)</option>
                      <option value="1024x1024">1024x1024 (Square)</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-xs text-white/60 mb-2">Duration</label>
                    <select 
                      value={videoParams.duration} 
                      onChange={(e) => setVideoParams({...videoParams, duration: parseInt(e.target.value)})}
                      className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm focus:border-cyan-500/50 focus:outline-none"
                    >
                      <option value="4">4 seconds</option>
                      <option value="8">8 seconds</option>
                      <option value="12">12 seconds</option>
                    </select>
                  </div>
                </div>
              )}
              
              <p className="text-xs text-white/40 mt-2">
                💡 Tip: {videoProvider === "runway" ? "Runway Gen-3 Turbo is faster, Gen-3 Alpha is higher quality" : "Longer videos and Pro quality take more time (2-5 minutes)"}
              </p>
            </div>
          )}

          <div className="mb-6">
            <p className="text-sm text-white/40 mb-3">Try these:</p>
            <div className="flex flex-wrap gap-2">
              {promptSuggestions[activeTab]?.map((suggestion, i) => (
                <button key={i} onClick={() => setPrompt(suggestion)} className="px-3 py-1.5 rounded-md bg-white/5 text-sm text-white/60 hover:bg-white/10 hover:text-white transition-colors">{suggestion}</button>
              ))}
            </div>
          </div>

          <button onClick={handleGenerate} disabled={generating} className="w-full btn-primary py-4 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50" data-testid="studio-generate-btn">
            {generating ? <><Loader2 className="w-5 h-5 animate-spin" /> {activeTab === "video" ? "Generating video (this may take 2-5 min)..." : "Generating..."}</> : <><Sparkles className="w-5 h-5" /> Generate {activeTab === "video" ? "Video" : activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</>}
          </button>
        </div>

        {result && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass rounded-xl p-6 md:p-8 mt-8">
            <div className="flex items-center gap-2 mb-4">
              <div className="status-active" />
              <h3 className="font-rajdhani text-lg font-semibold">Generated Content</h3>
              {result.provider && (
                <span className="ml-auto px-3 py-1 bg-cyan-500/20 text-cyan-400 text-xs rounded-full">
                  {result.provider === "sora_2" ? "Sora 2" : result.provider}
                </span>
              )}
            </div>
            
            {/* Display generated video */}
            {result.video_url && (
              <div className="mb-6 bg-black rounded-lg overflow-hidden">
                <video controls className="w-full max-h-[600px]" key={result.video_url}>
                  <source src={`${API.replace('/api', '')}${result.video_url}`} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
                {result.size && result.duration && (
                  <div className="p-3 bg-white/5 border-t border-white/10 flex items-center gap-4 text-xs text-white/60">
                    <span>📐 {result.size}</span>
                    <span>⏱️ {result.duration}s</span>
                    <span>🎬 {result.model}</span>
                  </div>
                )}
              </div>
            )}
            
            {/* Display generated image */}
            {result.image_data && <div className="mb-6"><img src={result.image_data} alt="Generated" className="max-w-full rounded-lg" /></div>}
            
            {/* Display generated audio */}
            {result.audio_url && (
              <div className="mb-6">
                <audio controls className="w-full">
                  <source src={result.audio_url} type="audio/mpeg" />
                </audio>
              </div>
            )}
            
            {/* Display text result */}
            {result.result && (
              <div className="bg-black/40 rounded-lg p-4 overflow-auto max-h-[500px] mb-6">
                <pre className="text-sm text-white/80 whitespace-pre-wrap font-manrope">{result.result}</pre>
              </div>
            )}
            
            {/* Action buttons */}
            <div className="flex gap-3 mt-6">
              <button 
                onClick={handleDownload}
                className="btn-primary px-6 py-2 rounded-md flex items-center gap-2"
              >
                <Download className="w-4 h-4" /> Download
              </button>
              <button 
                onClick={() => setShowPublishModal(true)}
                className="btn-secondary px-6 py-2 rounded-md flex items-center gap-2"
              >
                <Upload className="w-4 h-4" /> Publish to Market
              </button>
            </div>
          </motion.div>
        )}
        
        {/* Publish Modal */}
        {showPublishModal && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="glass rounded-2xl p-8 max-w-md w-full relative"
            >
              <button
                onClick={() => setShowPublishModal(false)}
                className="absolute top-4 right-4 p-2 rounded-lg hover:bg-white/10 transition"
              >
                <X className="w-5 h-5" />
              </button>
              
              <h2 className="font-rajdhani text-2xl font-bold mb-6">Publish to Marketplace</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="text-sm text-white/60 mb-2 block">Title *</label>
                  <input
                    type="text"
                    value={publishData.title}
                    onChange={(e) => setPublishData({...publishData, title: e.target.value})}
                    placeholder="My AI Creation"
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/30 focus:outline-none focus:border-cyan-500"
                  />
                </div>
                
                <div>
                  <label className="text-sm text-white/60 mb-2 block">Description</label>
                  <textarea
                    value={publishData.description}
                    onChange={(e) => setPublishData({...publishData, description: e.target.value})}
                    placeholder="Describe your creation..."
                    rows={3}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/30 focus:outline-none focus:border-cyan-500 resize-none"
                  />
                </div>
                
                <div>
                  <label className="text-sm text-white/60 mb-2 block">Price (USD)</label>
                  <input
                    type="number"
                    value={publishData.price}
                    onChange={(e) => setPublishData({...publishData, price: parseFloat(e.target.value)})}
                    min="0.99"
                    step="0.50"
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
                
                <div>
                  <label className="text-sm text-white/60 mb-2 block">Tags (comma separated)</label>
                  <input
                    type="text"
                    value={publishData.tags}
                    onChange={(e) => setPublishData({...publishData, tags: e.target.value})}
                    placeholder="ai, electronic, music"
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder:text-white/30 focus:outline-none focus:border-cyan-500"
                  />
                </div>
                
                <button
                  onClick={handlePublish}
                  className="w-full btn-primary px-6 py-3 rounded-lg font-semibold"
                >
                  Publish Now
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
};

// ==================== FEED PAGE ====================

export const FeedPage = () => {
  const { user, token } = useAuth();
  const queryClient = useQueryClient();
  const [newPost, setNewPost] = useState("");
  
  const { data: posts, refetch } = useQuery({ queryKey: ["posts"], queryFn: () => api.get("/posts") });

  const createPost = useMutation({
    mutationFn: (content) => api.post("/posts", { content, post_type: "text" }, token),
    onSuccess: () => { setNewPost(""); refetch(); toast.success("Post created!"); },
  });

  const likePost = useMutation({
    mutationFn: (postId) => api.post(`/posts/${postId}/like`, {}, token),
    onSuccess: () => refetch(),
  });

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6">
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="font-rajdhani text-4xl font-bold mb-2"><span className="gradient-text">Social Feed</span></h1>
          <p className="text-white/60">Connect with creators and discover trending content</p>
        </div>

        {user && (
          <div className="glass rounded-xl p-4 mb-8">
            <div className="flex gap-4">
              <img src={user.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.username}`} alt="" className="w-10 h-10 rounded-full" />
              <div className="flex-1">
                <textarea value={newPost} onChange={(e) => setNewPost(e.target.value)} placeholder="What's on your mind?" rows={3}
                  className="w-full bg-transparent border-none focus:outline-none text-white placeholder:text-white/30 resize-none" data-testid="feed-post-input" />
                <div className="flex items-center justify-between pt-3 border-t border-white/10">
                  <div className="flex gap-2">
                    <button className="p-2 rounded-md hover:bg-white/5 text-white/40"><Palette className="w-5 h-5" /></button>
                    <button className="p-2 rounded-md hover:bg-white/5 text-white/40"><Music className="w-5 h-5" /></button>
                    <button className="p-2 rounded-md hover:bg-white/5 text-white/40"><Video className="w-5 h-5" /></button>
                  </div>
                  <button onClick={() => createPost.mutate(newPost)} disabled={!newPost.trim() || createPost.isPending} className="btn-primary px-6 py-2 rounded-md disabled:opacity-50" data-testid="feed-post-btn">Post</button>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="space-y-4">
          {(posts || []).map((post) => (
            <motion.div key={post.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass rounded-xl p-4">
              <div className="flex gap-4">
                <Link to={`/profile/${post.author_id}`}>
                  <img src={post.author_avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${post.author_name}`} alt="" className="w-10 h-10 rounded-full" />
                </Link>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <Link to={`/profile/${post.author_id}`} className="font-semibold hover:text-cyan-400">{post.author_name}</Link>
                    <span className="text-white/40 text-sm">{new Date(post.created_at).toLocaleDateString()}</span>
                  </div>
                  <p className="text-white/80 mb-4 whitespace-pre-wrap">{post.content}</p>
                  <div className="flex items-center gap-6">
                    <button onClick={() => user && likePost.mutate(post.id)} className="flex items-center gap-2 text-white/40 hover:text-pink-400 transition-colors" data-testid={`post-like-${post.id}`}>
                      <Heart className="w-5 h-5" /> <span>{post.likes}</span>
                    </button>
                    <button className="flex items-center gap-2 text-white/40 hover:text-cyan-400"><MessageCircle className="w-5 h-5" /> <span>{post.comments_count}</span></button>
                    <button className="flex items-center gap-2 text-white/40 hover:text-green-400"><Share2 className="w-5 h-5" /> <span>{post.shares}</span></button>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {(!posts || posts.length === 0) && (
          <div className="text-center py-20">
            <Users className="w-16 h-16 text-white/20 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-2">No posts yet</h3>
            <p className="text-white/50">Be the first to share something!</p>
          </div>
        )}
      </div>
    </div>
  );
};

// ==================== SPOTLIGHT PAGE ====================

export const SpotlightPage = () => {
  const { data: spotlight } = useQuery({ queryKey: ["spotlight"], queryFn: () => api.get("/spotlight") });

  const awardIcons = { "Most Creative": Star, "Most Popular": TrendingUp, "Editor's Pick": Award, "Fastest Rising": Zap, "Best-Selling": DollarSign, "Featured Listing": Rocket };

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 mb-6">
            <Star className="w-4 h-4" /> <span className="text-sm font-semibold">Featured Daily</span>
          </div>
          <h1 className="font-rajdhani text-4xl md:text-5xl font-bold mb-4"><span className="gradient-text">Daily Spotlight</span></h1>
          <p className="text-white/60 max-w-2xl mx-auto">Every day, our AI curates the most impressive content. Featured creators get massive exposure.</p>
        </div>

        <div className="glass rounded-xl p-6 mb-10 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500/20 to-purple-500/20 flex items-center justify-center"><Rocket className="w-6 h-6 text-cyan-400" /></div>
            <div>
              <h3 className="font-semibold">Want to be featured?</h3>
              <p className="text-sm text-white/50">Boost your products starting at $5</p>
            </div>
          </div>
          <Link to="/marketplace" className="btn-primary px-6 py-3 rounded-lg flex items-center gap-2"><Rocket className="w-4 h-4" /> Boost a Product</Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {(spotlight || []).map((item, i) => {
            const AwardIcon = awardIcons[item.award_type] || Star;
            const isBoosted = item.is_boosted || item.award_type === "Featured Listing";
            return (
              <motion.div key={item.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }} className={`glass rounded-xl overflow-hidden card-hover ${isBoosted ? 'ring-2 ring-cyan-500/50' : ''}`}>
                {item.image_url && (
                  <div className="relative aspect-video">
                    <img src={item.image_url} alt={item.title} className="w-full h-full object-cover" />
                    {isBoosted && <div className="absolute top-3 right-3"><span className="px-2 py-1 rounded-md bg-gradient-to-r from-cyan-500/80 to-purple-500/80 text-white text-xs font-bold flex items-center gap-1"><Rocket className="w-3 h-3" /> BOOSTED</span></div>}
                  </div>
                )}
                <div className="p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${isBoosted ? 'bg-gradient-to-br from-cyan-500/20 to-purple-500/20' : 'bg-gradient-to-br from-yellow-500/20 to-orange-500/20'}`}>
                      <AwardIcon className={`w-5 h-5 ${isBoosted ? 'text-cyan-400' : 'text-yellow-400'}`} />
                    </div>
                    <span className={`text-sm font-semibold ${isBoosted ? 'text-cyan-400' : 'text-yellow-400'}`}>{item.award_type}</span>
                  </div>
                  <h3 className="font-rajdhani text-xl font-semibold mb-2">{item.title}</h3>
                  <p className="text-sm text-white/50 mb-4">by {item.creator_name}</p>
                  <div className="flex items-center justify-between">
                    <span className="px-3 py-1 rounded-full bg-white/5 text-sm capitalize">{item.content_type}</span>
                    <div className="flex items-center gap-4">
                      {item.price && <span className="text-cyan-400 font-semibold">${item.price}</span>}
                      <div className="flex items-center gap-2 text-white/60"><Heart className="w-4 h-4" /> <span>{item.votes?.toLocaleString()}</span></div>
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

// ==================== AGENTS PAGE ====================

export const AgentsPage = () => {
  const { user, token } = useAuth();
  const { data: agents, refetch } = useQuery({ queryKey: ["agents"], queryFn: () => api.get("/agents") });

  const runAgent = async (agentId) => {
    if (user?.role !== "admin") { toast.error("Admin access required"); return; }
    try {
      toast.loading("Running agent...");
      await axios.post(`${API}/agents/${agentId}/run`, {}, { headers: { Authorization: `Bearer ${token}` }});
      toast.dismiss();
      toast.success("Agent task completed!");
      refetch();
    } catch (err) { toast.dismiss(); toast.error(err.response?.data?.detail || "Failed to run agent"); }
  };

  const agentIcons = { 
    "CEO Agent": TrendingUp, 
    "Product Manager": Package, 
    "Marketing Agent": Share2, 
    "Vendor Manager": Users, 
    "Finance Agent": DollarSign,
    "Tool Discovery Agent": Sparkles,
    "Investor Outreach Agent": Rocket,
    "Marketing Automation": BarChart3,
    "Platform Optimizer": Settings,
    "CI/CD Agent": Zap,
    "AIxploria Discovery": Bot
  };

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6">
      <div className="max-w-5xl mx-auto">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-500/10 border border-green-500/30 text-green-400 mb-6">
            <Bot className="w-4 h-4" /> <span className="text-sm font-semibold">All Systems Active</span>
          </div>
          <h1 className="font-rajdhani text-4xl md:text-5xl font-bold mb-4"><span className="gradient-text">AI Agents Dashboard</span></h1>
          <p className="text-white/60 max-w-2xl mx-auto">11 autonomous AI agents running your marketplace 24/7. Now with multi-source discovery and Manus AI orchestration.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {(agents || []).map((agent, i) => {
            const Icon = agentIcons[agent.name] || Bot;
            const isManusAgent = agent.agent_type === "manus";
            const isAutonomous = agent.agent_type === "autonomous";
            const bgGradient = isAutonomous ? "bg-gradient-to-br from-cyan-500/20 to-blue-500/20" : 
                               isManusAgent ? "bg-gradient-to-br from-purple-500/20 to-pink-500/20" : 
                               "bg-gradient-to-br from-green-500/20 to-cyan-500/20";
            const textColor = isAutonomous ? "text-cyan-400" : isManusAgent ? "text-purple-400" : "text-green-400";
            const label = isAutonomous ? "Autonomous" : isManusAgent ? "Manus AI" : agent.status;
            
            return (
              <motion.div key={agent.id} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }} className="glass rounded-xl p-6 card-hover">
                <div className="flex items-start gap-4">
                  <div className={`w-14 h-14 rounded-xl ${bgGradient} flex items-center justify-center flex-shrink-0`}>
                    <Icon className={`w-7 h-7 ${textColor}`} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <div className="status-active status-pulse" />
                      <span className={`text-xs font-semibold uppercase tracking-wider ${textColor}`}>
                        {label}
                      </span>
                    </div>
                    <h3 className="font-rajdhani text-xl font-semibold">{agent.name}</h3>
                    <p className="text-sm text-white/40 mb-3">{agent.role}</p>
                    <p className="text-sm text-white/60 mb-4">{agent.description}</p>
                    
                    {agent.latest_report && (
                      <div className="p-3 rounded-lg bg-white/5 mb-4">
                        <p className="text-xs text-white/50 mb-1">Latest Report:</p>
                        <p className="text-sm text-white/70 line-clamp-3">{agent.latest_report}</p>
                      </div>
                    )}
                    
                    <div className="flex items-center justify-between pt-4 border-t border-white/10">
                      <div className="flex items-center gap-2 text-sm text-white/40">
                        <Zap className="w-4 h-4 text-cyan-400" />
                        <span className="text-cyan-400 font-semibold">{agent.tasks_completed} tasks</span>
                      </div>
                      {user?.role === "admin" && (
                        <button onClick={() => runAgent(agent.id)} className="btn-secondary px-3 py-1 rounded-md text-sm">Run Now</button>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Agent Stats */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-12">
          {[
            { label: "Total Agents", value: "11", icon: Bot, color: "cyan" },
            { label: "Tasks Completed", value: "12.5K+", icon: Zap, color: "green" },
            { label: "Uptime", value: "99.9%", icon: Clock, color: "purple" },
            { label: "Revenue Generated", value: "$42K", icon: DollarSign, color: "yellow" },
            { label: "Tools Integrated", value: "15+", icon: Settings, color: "pink" },
          ].map((stat, i) => (
            <div key={i} className="glass rounded-xl p-4 text-center">
              <stat.icon className={`w-6 h-6 text-${stat.color}-400 mx-auto mb-2`} />
              <div className="font-rajdhani text-2xl font-bold gradient-text">{stat.value}</div>
              <div className="text-sm text-white/50">{stat.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ==================== VENDOR PAGE ====================

export const VendorPage = () => {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [shopName, setShopName] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("digital");

  const createVendor = useMutation({
    mutationFn: () => api.post("/vendors", { shop_name: shopName, description, category }, token),
    onSuccess: () => { toast.success("Shop created!"); navigate("/marketplace"); },
    onError: (err) => toast.error(err.response?.data?.detail || "Failed"),
  });

  if (!user) {
    return (
      <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6 flex items-center justify-center">
        <div className="glass rounded-xl p-8 text-center max-w-md">
          <ShoppingCart className="w-16 h-16 text-cyan-400 mx-auto mb-4" />
          <h2 className="font-rajdhani text-2xl font-bold mb-2">Open Your Shop</h2>
          <p className="text-white/60 mb-6">Sign in to create your vendor account</p>
          <Link to="/login" className="btn-primary px-8 py-3 rounded-md inline-block">Sign In</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="font-rajdhani text-4xl md:text-5xl font-bold mb-4"><span className="gradient-text">Vendor Portal</span></h1>
          <p className="text-white/60">Open your shop in 60 seconds</p>
        </div>

        <div className="glass rounded-xl p-6 md:p-8">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-white/60 mb-2">Shop Name</label>
              <input type="text" value={shopName} onChange={(e) => setShopName(e.target.value)} placeholder="Enter your shop name"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-cyan-500/50 focus:outline-none text-white placeholder:text-white/30" data-testid="vendor-shop-name" />
            </div>
            <div>
              <label className="block text-sm font-medium text-white/60 mb-2">Description</label>
              <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Describe what you sell..." rows={4}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-cyan-500/50 focus:outline-none text-white placeholder:text-white/30 resize-none" data-testid="vendor-description" />
            </div>
            <div>
              <label className="block text-sm font-medium text-white/60 mb-2">Category</label>
              <select value={category} onChange={(e) => setCategory(e.target.value)}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-cyan-500/50 focus:outline-none text-white" data-testid="vendor-category">
                <option value="digital">Digital Products</option>
                <option value="music">Music & Audio</option>
                <option value="video">Video Content</option>
                <option value="ebook">eBooks & Writing</option>
                <option value="art">Digital Art</option>
                <option value="services">Services</option>
              </select>
            </div>
            <button onClick={() => createVendor.mutate()} disabled={!shopName.trim() || createVendor.isPending}
              className="w-full btn-primary py-4 rounded-lg flex items-center justify-center gap-2 disabled:opacity-50" data-testid="vendor-create-btn">
              {createVendor.isPending ? <><Loader2 className="w-5 h-5 animate-spin" /> Creating...</> : <><ShoppingCart className="w-5 h-5" /> Create Shop</>}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
          {[
            { icon: Zap, title: "Instant Setup", desc: "Your shop is live in 60 seconds" },
            { icon: Bot, title: "AI Management", desc: "AI agents handle operations" },
            { icon: DollarSign, title: "Auto Payouts", desc: "Daily profit deposits" },
          ].map((benefit, i) => (
            <div key={i} className="glass rounded-xl p-4 text-center">
              <benefit.icon className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
              <h3 className="font-semibold mb-1">{benefit.title}</h3>
              <p className="text-sm text-white/50">{benefit.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ==================== BOOST SUCCESS PAGE ====================

export const BoostSuccessPage = () => {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get("session_id");
  const [status, setStatus] = useState("checking");
  const [attempts, setAttempts] = useState(0);
  const navigate = useNavigate();

  React.useEffect(() => {
    if (!sessionId) { navigate("/marketplace"); return; }
    const poll = async () => {
      if (attempts >= 10) { setStatus("timeout"); return; }
      try {
        const res = await axios.get(`${API}/boost/status/${sessionId}`);
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
            <h2 className="font-rajdhani text-2xl font-bold mb-2">Boost Activated!</h2>
            <p className="text-white/60 mb-6">Your product is now featured!</p>
            <div className="space-y-3">
              <Link to="/spotlight" className="block w-full btn-primary py-3 rounded-lg">View Spotlight</Link>
              <Link to="/marketplace" className="block w-full btn-secondary py-3 rounded-lg">Back to Marketplace</Link>
            </div>
          </motion.div>
        )}
        {status === "expired" && (
          <div className="glass rounded-2xl p-8 text-center">
            <X className="w-16 h-16 text-red-400 mx-auto mb-6" />
            <h2 className="font-rajdhani text-2xl font-bold mb-2">Payment Expired</h2>
            <Link to="/marketplace" className="block w-full btn-secondary py-3 rounded-lg">Back to Marketplace</Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default { StudioPage, FeedPage, SpotlightPage, AgentsPage, VendorPage, BoostSuccessPage };
