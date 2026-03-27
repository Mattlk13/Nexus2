import React, { useState } from "react";
import { motion } from "framer-motion";
import axios from "axios";
import { Code, Send, Copy, CheckCircle, Zap, Book, Rocket, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { API, useAuth } from "../App";

export const APIPlaygroundPage = () => {
  const { token } = useAuth();
  const [selectedEndpoint, setSelectedEndpoint] = useState("stats");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  
  const endpoints = [
    {
      id: "stats",
      name: "Platform Stats",
      method: "GET",
      path: "/api/stats",
      auth: false,
      description: "Get platform statistics",
      example: {}
    },
    {
      id: "agents",
      name: "AI Agents",
      method: "GET",
      path: "/api/agents",
      auth: false,
      description: "Get all 46 AI agents",
      example: {}
    },
    {
      id: "mega-discovery",
      name: "Mega Discovery (Latest)",
      method: "GET",
      path: "/api/admin/mega-discovery/latest",
      auth: true,
      description: "Get latest mega scan results (109 tools from 9 sources)",
      example: {}
    },
    {
      id: "investor-dashboard",
      name: "Investor Dashboard",
      method: "GET",
      path: "/api/admin/investor-dashboard",
      auth: true,
      description: "Get investor metrics and 27-investor database",
      example: {}
    },
    {
      id: "enhanced-profile",
      name: "Enhanced Profile",
      method: "GET",
      path: "/api/users/user-1/profile/enhanced",
      auth: false,
      description: "Get detailed user profile with analytics",
      example: {}
    },
    {
      id: "mcp-status",
      name: "MCP Integration Status",
      method: "GET",
      path: "/api/admin/mcp/status",
      auth: true,
      description: "Get Model Context Protocol integration status",
      example: {}
    },
    {
      id: "marketing-seo",
      name: "SEO Performance",
      method: "GET",
      path: "/api/marketing/seo",
      auth: true,
      description: "Get SEO metrics and keyword rankings",
      example: {}
    }
  ];
  
  const testEndpoint = async () => {
    setLoading(true);
    setResponse(null);
    
    try {
      const endpoint = endpoints.find(e => e.id === selectedEndpoint);
      const config = endpoint.auth && token ? {
        headers: { Authorization: `Bearer ${token}` }
      } : {};
      
      const res = await axios({
        method: endpoint.method,
        url: `${API}${endpoint.path}`,
        ...config
      });
      
      setResponse({
        status: res.status,
        data: res.data
      });
      
      toast.success("API call successful!");
    } catch (err) {
      setResponse({
        status: err.response?.status || 500,
        error: err.response?.data?.detail || err.message
      });
      toast.error("API call failed");
    } finally {
      setLoading(false);
    }
  };
  
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    toast.success("Copied to clipboard!");
    setTimeout(() => setCopied(false), 2000);
  };
  
  const selectedEndpointData = endpoints.find(e => e.id === selectedEndpoint);
  
  return (
    <div className="min-h-screen pt-20 pb-10 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-10"
        >
          <h1 className="font-rajdhani text-4xl md:text-5xl font-bold mb-3 bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
            NEXUS API Playground
          </h1>
          <p className="text-white/60">Test and explore NEXUS API endpoints interactively</p>
          
          <div className="flex items-center justify-center gap-4 mt-6">
            <a 
              href="/NEXUS_API_DOCUMENTATION.md" 
              target="_blank"
              className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition flex items-center gap-2 text-sm"
            >
              <Book className="w-4 h-4" />
              View Documentation
            </a>
            <div className="px-4 py-2 rounded-lg bg-green-500/20 text-green-400 text-sm flex items-center gap-2">
              <Zap className="w-4 h-4" />
              46 AI Agents Active
            </div>
          </div>
        </motion.div>
        
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Endpoints List */}
          <div className="lg:col-span-1">
            <div className="glass rounded-xl p-6 sticky top-24">
              <h2 className="font-rajdhani text-xl font-bold mb-4">Endpoints</h2>
              <div className="space-y-2">
                {endpoints.map((endpoint) => (
                  <button
                    key={endpoint.id}
                    onClick={() => setSelectedEndpoint(endpoint.id)}
                    className={`w-full text-left p-3 rounded-lg transition ${
                      selectedEndpoint === endpoint.id
                        ? "bg-cyan-500/20 border border-cyan-500/50"
                        : "bg-white/5 border border-white/10 hover:bg-white/10"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-sm">{endpoint.name}</span>
                      <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                        endpoint.method === 'GET' ? 'bg-green-500/20 text-green-400' : 'bg-blue-500/20 text-blue-400'
                      }`}>
                        {endpoint.method}
                      </span>
                    </div>
                    <div className="text-xs text-white/50 font-mono">{endpoint.path}</div>
                    {endpoint.auth && (
                      <div className="text-xs text-yellow-400 mt-1">🔒 Auth required</div>
                    )}
                  </button>
                ))}
              </div>
            </div>
          </div>
          
          {/* Request/Response Panel */}
          <div className="lg:col-span-2 space-y-6">
            {/* Request */}
            <div className="glass rounded-xl p-6">
              <h2 className="font-rajdhani text-xl font-bold mb-4">Request</h2>
              
              <div className="space-y-4">
                <div>
                  <div className="text-sm text-white/60 mb-2">Endpoint</div>
                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 rounded-lg font-bold text-sm ${
                      selectedEndpointData?.method === 'GET' ? 'bg-green-500/20 text-green-400' : 'bg-blue-500/20 text-blue-400'
                    }`}>
                      {selectedEndpointData?.method}
                    </span>
                    <code className="flex-1 px-4 py-2 bg-black/40 rounded-lg text-cyan-400 text-sm font-mono">
                      {selectedEndpointData?.path}
                    </code>
                    <button
                      onClick={() => copyToClipboard(selectedEndpointData?.path)}
                      className="p-2 rounded-lg hover:bg-white/10 transition"
                    >
                      {copied ? <CheckCircle className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
                
                <div>
                  <div className="text-sm text-white/60 mb-2">Description</div>
                  <p className="text-white/80">{selectedEndpointData?.description}</p>
                </div>
                
                {selectedEndpointData?.auth && (
                  <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30 text-sm text-yellow-400">
                    🔒 This endpoint requires authentication. {token ? "You are logged in." : "Please login first."}
                  </div>
                )}
                
                <button
                  onClick={testEndpoint}
                  disabled={loading || (selectedEndpointData?.auth && !token)}
                  className="w-full btn-primary px-6 py-3 rounded-lg font-semibold flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                  {loading ? "Calling API..." : "Send Request"}
                </button>
              </div>
            </div>
            
            {/* Response */}
            {response && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass rounded-xl p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-rajdhani text-xl font-bold">Response</h2>
                  <div className={`px-3 py-1 rounded-lg font-bold text-sm ${
                    response.status === 200 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                  }`}>
                    {response.status} {response.status === 200 ? 'OK' : 'Error'}
                  </div>
                </div>
                
                <div className="bg-black/60 rounded-lg p-4 overflow-auto max-h-[600px]">
                  <pre className="text-sm text-cyan-400 font-mono">
                    {JSON.stringify(response.data || response.error, null, 2)}
                  </pre>
                </div>
                
                <button
                  onClick={() => copyToClipboard(JSON.stringify(response.data || response.error, null, 2))}
                  className="mt-4 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 transition flex items-center gap-2 text-sm"
                >
                  {copied ? <CheckCircle className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                  Copy Response
                </button>
              </motion.div>
            )}
            
            {/* Quick Stats */}
            {!response && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="glass rounded-xl p-4">
                  <Rocket className="w-8 h-8 text-cyan-400 mb-2" />
                  <div className="text-2xl font-bold">109</div>
                  <div className="text-xs text-white/60">Tools Discovered</div>
                </div>
                <div className="glass rounded-xl p-4">
                  <Code className="w-8 h-8 text-purple-400 mb-2" />
                  <div className="text-2xl font-bold">100+</div>
                  <div className="text-xs text-white/60">API Endpoints</div>
                </div>
                <div className="glass rounded-xl p-4">
                  <Zap className="w-8 h-8 text-green-400 mb-2" />
                  <div className="text-2xl font-bold">46</div>
                  <div className="text-xs text-white/60">AI Agents</div>
                </div>
                <div className="glass rounded-xl p-4">
                  <Book className="w-8 h-8 text-orange-400 mb-2" />
                  <div className="text-2xl font-bold">27</div>
                  <div className="text-xs text-white/60">Investors in DB</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
