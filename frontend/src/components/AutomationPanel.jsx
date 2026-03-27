import React, { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { toast } from "sonner";
import axios from "axios";
import {
  Loader2, AlertCircle, Sparkles, Zap, Rocket
} from "lucide-react";
import { API } from "../App";

export const AutomationPanel = ({ token }) => {
  const [discovering, setDiscovering] = useState(false);
  const [scanningAixploria, setScanningAixploria] = useState(false);
  const [comprehensiveScan, setComprehensiveScan] = useState(false);
  const [activeSubTab, setActiveSubTab] = useState("aixploria");
  const queryClient = useQueryClient();
  
  const { data: discoveredTools } = useQuery({
    queryKey: ["discovered-tools"],
    queryFn: () => axios.get(`${API}/automation/discovered-tools`, { headers: { Authorization: `Bearer ${token}` }}).then(r => r.data),
  });
  
  const { data: aixploriaTools } = useQuery({
    queryKey: ["aixploria-tools"],
    queryFn: () => axios.get(`${API}/admin/aixploria/tools`, { headers: { Authorization: `Bearer ${token}` }}).then(r => r.data),
    refetchInterval: 30000
  });
  
  const { data: aixploriaStats } = useQuery({
    queryKey: ["aixploria-stats"],
    queryFn: () => axios.get(`${API}/admin/aixploria/stats`, { headers: { Authorization: `Bearer ${token}` }}).then(r => r.data),
  });
  
  const { data: manusStatus } = useQuery({
    queryKey: ["manus-status"],
    queryFn: async () => {
      try {
        const res = await axios.post(`${API}/manus/task`, 
          { description: "Health check", context: {} },
          { headers: { Authorization: `Bearer ${token}` }}
        );
        return { connected: !res.data.mocked, ...res.data };
      } catch {
        return { connected: false };
      }
    },
    refetchInterval: 60000
  });
  
  const { data: integrationStatus } = useQuery({
    queryKey: ["integration-status"],
    queryFn: () => axios.get(`${API}/integrations/status`, { headers: { Authorization: `Bearer ${token}` }}).then(r => r.data),
    refetchInterval: 30000
  });
  
  const { data: openclawStatus } = useQuery({
    queryKey: ["openclaw-status"],
    queryFn: () => axios.get(`${API}/admin/openclaw/status`, { headers: { Authorization: `Bearer ${token}` }}).then(r => r.data),
    refetchInterval: 30000
  });
  
  const { data: openclawAnalysis } = useQuery({
    queryKey: ["openclaw-analysis"],
    queryFn: () => axios.get(`${API}/admin/openclaw/analysis`, { headers: { Authorization: `Bearer ${token}` }}).then(r => r.data),
  });
  
  const triggerDiscovery = async () => {
    setDiscovering(true);
    try {
      toast.loading("Discovering tools across GitHub...");
      await axios.post(
        `${API}/automation/discover-tools`,
        ["marketing", "investor_tools", "admin_dashboard", "payments", "ai_tools", "automation"],
        { headers: { Authorization: `Bearer ${token}` }}
      );
      toast.dismiss();
      toast.success("Tool discovery completed!");
      queryClient.invalidateQueries(["discovered-tools"]);
    } catch (err) {
      toast.dismiss();
      toast.error("Discovery failed");
    } finally {
      setDiscovering(false);
    }
  };
  
  const triggerAixploriaScan = async () => {
    setScanningAixploria(true);
    try {
      const scanType = comprehensiveScan ? "all 50+ categories" : "top & latest";
      toast.loading(`Scanning ${scanType}...`);
      
      const response = await axios.post(
        `${API}/admin/aixploria/scan${comprehensiveScan ? '?comprehensive=true' : ''}`,
        {},
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      toast.dismiss();
      const time = response.data.estimated_time || "30 seconds";
      toast.success(`Multi-source discovery started! Expected time: ${time}`);
      
      setTimeout(() => {
        queryClient.invalidateQueries(["aixploria-tools"]);
        queryClient.invalidateQueries(["aixploria-stats"]);
      }, comprehensiveScan ? 120000 : 15000);  // 2 mins for comprehensive, 15s for standard
    } catch (err) {
      toast.dismiss();
      toast.error("Scan failed");
    } finally {
      setScanningAixploria(false);
    }
  };
  
  const getBenefitColor = (level) => {
    switch(level) {
      case "critical": return "bg-red-500/20 text-red-400 border-red-500/30";
      case "high": return "bg-orange-500/20 text-orange-400 border-orange-500/30";
      case "medium": return "bg-blue-500/20 text-blue-400 border-blue-500/30";
      default: return "bg-gray-500/20 text-gray-400 border-gray-500/30";
    }
  };
  
  return (
    <div className="space-y-6">
      {/* Sub-tabs */}
      <div className="flex gap-2 border-b border-white/10 pb-2 overflow-x-auto">
        <button
          onClick={() => setActiveSubTab("aixploria")}
          className={`px-4 py-2 rounded-lg text-sm font-semibold transition whitespace-nowrap ${activeSubTab === "aixploria" ? "bg-cyan-500/20 text-cyan-400" : "text-white/50 hover:text-white/80"}`}
        >
          🌐 AIxploria
        </button>
        <button
          onClick={() => setActiveSubTab("mega")}
          className={`px-4 py-2 rounded-lg text-sm font-semibold transition whitespace-nowrap ${activeSubTab === "mega" ? "bg-cyan-500/20 text-cyan-400" : "text-white/50 hover:text-white/80"}`}
        >
          🚀 Mega Discovery
        </button>
        <button
          onClick={() => setActiveSubTab("mcp")}
          className={`px-4 py-2 rounded-lg text-sm font-semibold transition whitespace-nowrap ${activeSubTab === "mcp" ? "bg-cyan-500/20 text-cyan-400" : "text-white/50 hover:text-white/80"}`}
        >
          🔌 MCP Servers
        </button>
        <button
          onClick={() => setActiveSubTab("github")}
          className={`px-4 py-2 rounded-lg text-sm font-semibold transition whitespace-nowrap ${activeSubTab === "github" ? "bg-cyan-500/20 text-cyan-400" : "text-white/50 hover:text-white/80"}`}
        >
          🐙 GitHub
        </button>
        <button
          onClick={() => setActiveSubTab("openclaw")}
          className={`px-4 py-2 rounded-lg text-sm font-semibold transition whitespace-nowrap ${activeSubTab === "openclaw" ? "bg-cyan-500/20 text-cyan-400" : "text-white/50 hover:text-white/80"}`}
        >
          🦾 OpenClaw
        </button>
        <button
          onClick={() => setActiveSubTab("manus")}
          className={`px-4 py-2 rounded-lg text-sm font-semibold transition whitespace-nowrap ${activeSubTab === "manus" ? "bg-cyan-500/20 text-cyan-400" : "text-white/50 hover:text-white/80"}`}
        >
          🔮 Manus AI
        </button>
        <button
          onClick={() => setActiveSubTab("integrations")}
          className={`px-4 py-2 rounded-lg text-sm font-semibold transition whitespace-nowrap ${activeSubTab === "integrations" ? "bg-cyan-500/20 text-cyan-400" : "text-white/50 hover:text-white/80"}`}
        >
          🔌 Integrations
        </button>
        <button
          onClick={() => setActiveSubTab("marketing")}
          className={`px-4 py-2 rounded-lg text-sm font-semibold transition whitespace-nowrap ${activeSubTab === "marketing" ? "bg-cyan-500/20 text-cyan-400" : "text-white/50 hover:text-white/80"}`}
        >
          📢 Marketing
        </button>
        <button
          onClick={() => setActiveSubTab("cloudflare")}
          className={`px-4 py-2 rounded-lg text-sm font-semibold transition whitespace-nowrap ${activeSubTab === "cloudflare" ? "bg-cyan-500/20 text-cyan-400" : "text-white/50 hover:text-white/80"}`}
        >
          ☁️ Edge Workers
        </button>
      </div>
      
      {/* AIxploria Tab */}
      {activeSubTab === "aixploria" && (
        <div className="space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="glass rounded-xl p-4">
              <div className="text-3xl font-bold text-cyan-400">{aixploriaStats?.total_scans || 0}</div>
              <div className="text-sm text-white/60 mt-1">Total Scans</div>
            </div>
            <div className="glass rounded-xl p-4">
              <div className="text-3xl font-bold text-red-400">{aixploriaStats?.critical_count || 0}</div>
              <div className="text-sm text-white/60 mt-1">Critical</div>
            </div>
            <div className="glass rounded-xl p-4">
              <div className="text-3xl font-bold text-orange-400">{aixploriaStats?.high_count || 0}</div>
              <div className="text-sm text-white/60 mt-1">High Priority</div>
            </div>
            <div className="glass rounded-xl p-4">
              <div className="text-3xl font-bold text-purple-400">{aixploriaTools?.total || 0}</div>
              <div className="text-sm text-white/60 mt-1">Total Tools</div>
            </div>
          </div>
          
          {/* Scan Control */}
          <div className="glass rounded-xl p-6">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-4">
              <div className="flex-1">
                <h3 className="font-rajdhani text-xl font-bold">Multi-Source AI Discovery</h3>
                <p className="text-sm text-white/60">Scans AIxploria, GitHub Trending, ProductHunt</p>
                {aixploriaStats?.last_scan && (
                  <p className="text-xs text-cyan-400 mt-1">
                    Last: {new Date(aixploriaStats.last_scan).toLocaleString()}
                  </p>
                )}
              </div>
              <div className="flex flex-col items-end gap-3">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="comprehensive"
                    checked={comprehensiveScan}
                    onChange={(e) => setComprehensiveScan(e.target.checked)}
                    className="w-4 h-4 rounded border-white/20 bg-white/10 text-cyan-500 focus:ring-cyan-500"
                  />
                  <label htmlFor="comprehensive" className="text-sm text-white/80 cursor-pointer">
                    Comprehensive (All 50+ categories)
                  </label>
                </div>
                <button 
                  onClick={triggerAixploriaScan} 
                  disabled={scanningAixploria}
                  className="btn-primary px-6 py-3 rounded-lg flex items-center gap-2 disabled:opacity-50"
                >
                  {scanningAixploria ? <Loader2 className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
                  {scanningAixploria ? "Scanning..." : "Scan Now"}
                </button>
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center gap-2 p-3 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-sm text-cyan-400">
                <Sparkles className="w-4 h-4 flex-shrink-0" />
                <span>Automated daily scans at 2:00 AM UTC</span>
              </div>
              {comprehensiveScan && (
                <div className="flex items-center gap-2 p-3 rounded-lg bg-purple-500/10 border border-purple-500/30 text-sm text-purple-400">
                  <Zap className="w-4 h-4 flex-shrink-0" />
                  <span>Comprehensive mode: Scans 50+ categories (2-3 mins, ~250+ tools)</span>
                </div>
              )}
            </div>
          </div>
          
          {/* Tools List */}
          <div className="glass rounded-xl p-6">
            <h3 className="font-rajdhani text-xl font-bold mb-4">Discovered AI Tools</h3>
            
            {aixploriaTools?.tools && aixploriaTools.tools.length > 0 ? (
              <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
                {aixploriaTools.tools.map((tool, i) => (
                  <motion.div 
                    key={i}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.03 }}
                    className="p-4 rounded-lg bg-white/5 border border-white/10 hover:border-cyan-500/50 transition"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2 flex-wrap">
                          <h4 className="font-semibold text-base">{tool.name}</h4>
                          <span className={`px-2 py-1 rounded text-xs font-semibold border ${getBenefitColor(tool.benefit_level)}`}>
                            {tool.benefit_level?.toUpperCase()}
                          </span>
                          {tool.recommendation && (
                            <span className="px-2 py-1 rounded text-xs bg-purple-500/20 text-purple-400">
                              {tool.recommendation.replace(/_/g, ' ')}
                            </span>
                          )}
                        </div>
                        
                        {tool.description && (
                          <p className="text-sm text-white/70 mb-3">{tool.description}</p>
                        )}
                        
                        <div className="flex flex-wrap gap-2 mb-3">
                          {(tool.nexus_categories || []).map((cat, j) => (
                            <span key={j} className="text-xs px-2 py-1 rounded bg-white/5 text-white/60">
                              {cat}
                            </span>
                          ))}
                        </div>
                        
                        {(tool.reasons || []).length > 0 && (
                          <div className="space-y-1">
                            {tool.reasons.map((reason, j) => (
                              <div key={j} className="flex items-center gap-2 text-xs text-cyan-400">
                                <div className="w-1 h-1 rounded-full bg-cyan-400"></div>
                                {reason}
                              </div>
                            ))}
                          </div>
                        )}
                        
                        <div className="flex items-center gap-3 mt-3 text-xs text-white/40 flex-wrap">
                          <span>Source: {tool.source}</span>
                          <span>•</span>
                          <span>Category: {tool.category}</span>
                          {tool.stars && (
                            <>
                              <span>•</span>
                              <span>⭐ {tool.stars}</span>
                            </>
                          )}
                        </div>
                      </div>
                      
                      <div className="text-right flex flex-col items-end gap-2">
                        <div className="flex items-center gap-2">
                          <div className="text-xs text-white/40">Score</div>
                          <div className="text-2xl font-bold text-cyan-400">{tool.nexus_score}</div>
                        </div>
                        {tool.url && (
                          <a 
                            href={tool.url.startsWith('http') ? tool.url : `https://${tool.url}`}
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="text-xs text-cyan-400 hover:text-cyan-300 underline"
                          >
                            View Tool →
                          </a>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="text-center py-16 text-white/50">
                <Rocket className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p className="text-base mb-2">No AI tools discovered yet</p>
                <p className="text-sm">Run a scan to discover AI tools from multiple sources</p>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* GitHub Tab */}
      {activeSubTab === "github" && (
        <div className="glass rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="font-rajdhani text-2xl font-bold">GitHub Repository Discovery</h2>
              <p className="text-white/60 text-sm">Search GitHub for beneficial integrations</p>
            </div>
            <button 
              onClick={triggerDiscovery} 
              disabled={discovering}
              className="btn-primary px-4 py-2 rounded-md flex items-center gap-2 disabled:opacity-50"
            >
              {discovering ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              {discovering ? "Discovering..." : "Search GitHub"}
            </button>
          </div>
          
          <div className="space-y-3 max-h-[600px] overflow-y-auto">
            {(discoveredTools?.tools || []).slice(0, 15).map((tool, i) => (
              <div key={i} className="p-4 rounded-lg bg-white/5 border border-white/10 hover:border-cyan-500/50 transition">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold">{tool.tool?.name || "Unknown"}</h3>
                      <span className={`px-2 py-0.5 rounded text-xs ${tool.benefit_level === "high" ? "bg-green-500/20 text-green-400" : "bg-blue-500/20 text-blue-400"}`}>
                        {tool.benefit_level}
                      </span>
                    </div>
                    <p className="text-sm text-white/60 mb-2">{tool.tool?.description}</p>
                    <div className="flex flex-wrap gap-2">
                      {(tool.reasons || []).map((reason, j) => (
                        <span key={j} className="text-xs text-cyan-400">• {reason}</span>
                      ))}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-cyan-400">{tool.score}</div>
                    <div className="text-xs text-white/40">score</div>
                  </div>
                </div>
              </div>
            ))}
            
            {(!discoveredTools?.tools || discoveredTools.tools.length === 0) && (
              <div className="text-center py-12 text-white/50">
                <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No tools yet. Run GitHub discovery.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* OpenClaw Tab */}
      {activeSubTab === "openclaw" && (
        <div className="glass rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="font-rajdhani text-2xl font-bold">OpenClaw Autonomous Agent</h2>
              <p className="text-white/60 text-sm">Self-improving platform intelligence</p>
            </div>
            <div className={`px-3 py-1 rounded-full text-sm font-semibold ${
              openclawStatus?.running ? "bg-green-500/20 text-green-400" : 
              openclawStatus?.installed ? "bg-blue-500/20 text-blue-400" : 
              "bg-gray-500/20 text-gray-400"
            }`}>
              {openclawStatus?.running ? "🟢 Running" : 
               openclawStatus?.installed ? "⚪ Ready" : 
               "⚫ Not Installed"}
            </div>
          </div>
          
          <div className="space-y-6">
            {/* Status Card */}
            <div className="p-4 rounded-lg bg-white/5 border border-white/10">
              <div className="flex items-start gap-3">
                <div className="text-3xl">🦾</div>
                <div className="flex-1">
                  <div className="font-semibold text-white mb-1">{openclawStatus?.message || "Checking status..."}</div>
                  <div className="text-sm text-white/60">{openclawStatus?.status}</div>
                  {openclawStatus?.recommendation && (
                    <div className="mt-2 p-2 rounded bg-blue-500/10 text-xs text-blue-400">
                      💡 {openclawStatus.recommendation}
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            {/* Capabilities */}
            {openclawStatus?.capabilities && (
              <div>
                <h3 className="text-sm font-semibold text-white/80 mb-3">Autonomous Capabilities</h3>
                <div className="grid grid-cols-1 gap-2">
                  {openclawStatus.capabilities.map((capability, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm text-white/70">
                      <Zap className="w-4 h-4 text-cyan-400" />
                      {capability}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Platform Analysis */}
            {openclawAnalysis?.suggestions && (
              <div>
                <h3 className="text-sm font-semibold text-white/80 mb-3">
                  Platform Improvement Suggestions
                  <span className="ml-2 text-xs text-white/50">
                    (Score: {openclawAnalysis.platform_score}/100)
                  </span>
                </h3>
                <div className="space-y-3">
                  {openclawAnalysis.suggestions.map((suggestion, i) => (
                    <div key={i} className="p-4 rounded-lg bg-white/5 border border-white/10 hover:border-cyan-500/30 transition">
                      <div className="flex items-start justify-between mb-2">
                        <div className="font-semibold text-white">{suggestion.title}</div>
                        <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                          suggestion.priority === 'high' ? 'bg-red-500/20 text-red-400' :
                          suggestion.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-green-500/20 text-green-400'
                        }`}>
                          {suggestion.priority}
                        </span>
                      </div>
                      <p className="text-sm text-white/70 mb-2">{suggestion.description}</p>
                      <div className="flex items-center gap-4 text-xs">
                        <span className="text-cyan-400">⚡ Impact: {suggestion.impact}</span>
                        <span className="text-white/50">⏱️ Effort: {suggestion.effort}</span>
                        <span className="text-purple-400">📦 Type: {suggestion.type}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Setup Instructions */}
            {!openclawStatus?.installed && (
              <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
                <div className="flex items-start gap-3">
                  <Rocket className="w-5 h-5 text-blue-400 mt-1 flex-shrink-0" />
                  <div>
                    <div className="font-semibold text-blue-400 mb-2">Setup OpenClaw</div>
                    <p className="text-sm text-white/70 mb-3">
                      Enable autonomous platform improvements by running the setup script:
                    </p>
                    <code className="block p-3 rounded bg-black/30 text-xs text-cyan-400 mb-3">
                      bash /app/setup_openclaw.sh
                    </code>
                    <p className="text-xs text-white/50">
                      Requires: Anthropic API key for Claude Sonnet 4
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      
      {/* Manus AI Tab */}
      {activeSubTab === "manus" && (
        <div className="glass rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="font-rajdhani text-2xl font-bold">Manus AI Orchestration</h2>
              <p className="text-white/60 text-sm">Autonomous agent layer</p>
            </div>
            <div className={`px-3 py-1 rounded-full text-sm font-semibold ${manusStatus?.connected ? "bg-green-500/20 text-green-400" : "bg-yellow-500/20 text-yellow-400"}`}>
              {manusStatus?.connected ? "✓ Connected" : "⚠ Demo"}
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="p-4 rounded-lg bg-white/5">
              <div className="text-2xl font-bold text-cyan-400">5</div>
              <div className="text-sm text-white/50">Manus Agents</div>
            </div>
            <div className="p-4 rounded-lg bg-white/5">
              <div className="text-2xl font-bold text-purple-400">24/7</div>
              <div className="text-sm text-white/50">Autonomous</div>
            </div>
          </div>
          
          {!manusStatus?.connected && (
            <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30 text-sm text-yellow-400">
              <div className="flex items-start gap-2">
                <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                <div>
                  <div className="font-semibold mb-1">API Key Required</div>
                  <div>Add MANUS_API_KEY to backend/.env</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Integrations Tab - Enhanced with real API status */}
      {activeSubTab === "integrations" && (
        <div className="glass rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-rajdhani text-2xl font-bold">Active Integrations</h2>
            {integrationStatus?.summary && (
              <div className="text-sm">
                <span className="text-white/50">Health: </span>
                <span className={`font-semibold ${
                  integrationStatus.summary.health_score >= 80 ? 'text-green-400' :
                  integrationStatus.summary.health_score >= 60 ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {integrationStatus.summary.health_score.toFixed(0)}%
                </span>
                <span className="text-white/50 ml-2">({integrationStatus.summary.active}/{integrationStatus.summary.total})</span>
              </div>
            )}
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {integrationStatus?.integrations ? (
              Object.entries(integrationStatus.integrations).map(([key, integration]) => (
                <div key={key} className="p-4 rounded-lg bg-white/5 border border-white/10 hover:border-cyan-500/30 transition">
                  <div className="flex items-start justify-between mb-2">
                    <div className="text-2xl">{getIntegrationIcon(key)}</div>
                    <div className={`text-xs font-semibold px-2 py-1 rounded ${
                      integration.active ? "bg-green-500/20 text-green-400" :
                      integration.status === "demo_mode" ? "bg-yellow-500/20 text-yellow-400" :
                      integration.status === "limited" ? "bg-orange-500/20 text-orange-400" :
                      "bg-red-500/20 text-red-400"
                    }`}>
                      {integration.active ? "● Active" :
                       integration.status === "demo_mode" ? "● Demo" :
                       integration.status === "limited" ? "● Limited" :
                       "● Missing"}
                    </div>
                  </div>
                  <div className="font-semibold text-sm mb-1">{integration.name}</div>
                  <div className="text-xs text-white/50 mb-2">{integration.description}</div>
                  {integration.rate_limit && (
                    <div className="text-xs text-cyan-400 mt-2">{integration.rate_limit}</div>
                  )}
                  {integration.demo_behavior && !integration.active && (
                    <div className="text-xs text-yellow-400/70 mt-2">⚠️ {integration.demo_behavior}</div>
                  )}
                </div>
              ))
            ) : (
              // Fallback to static list if API not available
              [
                { name: "Stripe", status: "active", icon: "💳", desc: "Payments" },
                { name: "OpenAI GPT-5.2", status: "active", icon: "🤖", desc: "Text gen" },
                { name: "Claude Sonnet 4", status: "active", icon: "🧠", desc: "Moderation" },
                { name: "Gemini Nano Banana", status: "active", icon: "🎨", desc: "Images" },
                { name: "Resend", status: "demo", icon: "📧", desc: "Emails" },
                { name: "Manus AI", status: manusStatus?.connected ? "active" : "demo", icon: "🔮", desc: "Agents" },
                { name: "GitHub", status: "demo", icon: "🐙", desc: "Repos" },
                { name: "GitLab", status: "demo", icon: "🦊", desc: "CI/CD" },
                { name: "AIxploria", status: "active", icon: "🌐", desc: "Discovery" },
                { name: "Softr", status: "active", icon: "🗄️", desc: "Database" },
              ].map((int) => (
                <div key={int.name} className="p-4 rounded-lg bg-white/5 border border-white/10 hover:border-cyan-500/30 transition">
                  <div className="text-3xl mb-2">{int.icon}</div>
                  <div className="font-semibold text-sm mb-1">{int.name}</div>
                  <div className="text-xs text-white/50 mb-2">{int.desc}</div>
                  <div className={`text-xs font-semibold ${int.status === "active" ? "text-green-400" : "text-yellow-400"}`}>
                    {int.status === "active" ? "● Active" : "● Demo"}
                  </div>
                </div>
              ))
            )}
          </div>
          
          {integrationStatus?.summary?.critical_missing?.length > 0 && (
            <div className="mt-6 p-4 rounded-lg bg-red-500/10 border border-red-500/30">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <div className="font-semibold text-red-400 mb-1">Critical Integrations Missing</div>
                  <div className="text-sm text-white/70">
                    {integrationStatus.summary.critical_missing.join(", ")} need to be configured for full functionality.
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
      
      {/* Mega Discovery Tab */}
      {activeSubTab === "mega" && (
        <MegaDiscoveryTab token={token} />
      )}
      
      {/* MCP Servers Tab */}
      {activeSubTab === "mcp" && (
        <MCPServersTab token={token} />
      )}
      
      {/* Marketing Automation Tab */}
      {activeSubTab === "marketing" && (
        <MarketingTab token={token} />
      )}
      
      {/* Cloudflare Workers Tab */}
      {activeSubTab === "cloudflare" && (
        <CloudflareTab token={token} />
      )}
    </div>
  );
};

// ==================== MEGA DISCOVERY TAB ====================
const MegaDiscoveryTab = ({ token }) => {
  const [discovering, setDiscovering] = useState(false);
  const queryClient = useQueryClient();
  
  const { data: megaScan } = useQuery({
    queryKey: ["mega-scan-latest"],
    queryFn: () => axios.get(`${API}/admin/mega-discovery/latest`, { 
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.data),
    refetchInterval: 30000
  });
  
  const triggerMegaDiscovery = async () => {
    setDiscovering(true);
    try {
      toast.loading("🚀 Mega Discovery initiated - scanning 9 sources...", { duration: 5000 });
      const res = await axios.post(
        `${API}/admin/mega-discovery`,
        {},
        { headers: { Authorization: `Bearer ${token}` }}
      );
      toast.dismiss();
      toast.success(`✓ Mega Discovery complete: ${res.data.total_discovered || 0} tools found!`);
      queryClient.invalidateQueries(["mega-scan-latest"]);
    } catch (err) {
      toast.dismiss();
      toast.error(err.response?.data?.detail || "Discovery failed");
    }
    setDiscovering(false);
  };
  
  const sources = megaScan?.results?.sources || {};
  const totalDiscovered = megaScan?.total_discovered || 0;
  
  return (
    <div className="space-y-6">
      {/* Mega Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass rounded-xl p-4">
          <div className="text-3xl font-bold text-purple-400">{totalDiscovered}</div>
          <div className="text-sm text-white/60 mt-1">Total Discovered</div>
        </div>
        <div className="glass rounded-xl p-4">
          <div className="text-3xl font-bold text-cyan-400">{Object.keys(sources).length}</div>
          <div className="text-sm text-white/60 mt-1">Sources Scanned</div>
        </div>
        <div className="glass rounded-xl p-4">
          <div className="text-3xl font-bold text-green-400">
            {sources.github?.count || 0}
          </div>
          <div className="text-sm text-white/60 mt-1">GitHub Tools</div>
        </div>
        <div className="glass rounded-xl p-4">
          <div className="text-3xl font-bold text-orange-400">
            {sources.npm?.count || 0}
          </div>
          <div className="text-sm text-white/60 mt-1">NPM Packages</div>
        </div>
      </div>
      
      {/* Scan Control */}
      <div className="glass rounded-xl p-6">
        <div className="flex items-start justify-between gap-4 mb-4">
          <div>
            <h3 className="font-rajdhani text-xl font-bold">Multi-Source Discovery Engine</h3>
            <p className="text-sm text-white/60 mt-1">
              Scans GitHub, GitLab, NPM, PyPI, Maven, MCP Servers, Cloudflare, Eclipse, SourceForge
            </p>
            {megaScan?.scan_timestamp && (
              <p className="text-xs text-cyan-400 mt-2">
                Last scan: {new Date(megaScan.scan_timestamp).toLocaleString()}
              </p>
            )}
          </div>
          <button 
            onClick={triggerMegaDiscovery}
            disabled={discovering}
            className="btn-primary px-6 py-3 rounded-lg flex items-center gap-2 disabled:opacity-50 shrink-0"
          >
            {discovering ? <Loader2 className="w-5 h-5 animate-spin" /> : <Rocket className="w-5 h-5" />}
            {discovering ? "Scanning..." : "Run Mega Scan"}
          </button>
        </div>
        
        <div className="space-y-2">
          <div className="p-3 rounded-lg bg-purple-500/10 border border-purple-500/30 text-sm text-purple-400">
            <Sparkles className="w-4 h-4 inline mr-2" />
            Discovers tools from 9+ sources in parallel (~3-5 mins)
          </div>
        </div>
      </div>
      
      {/* Source Results */}
      {megaScan?.results?.sources && (
        <div className="glass rounded-xl p-6">
          <h3 className="font-rajdhani text-xl font-bold mb-4">Discovery Results by Source</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(sources).map(([sourceName, sourceData]) => (
              <div key={sourceName} className="p-4 rounded-lg bg-white/5 border border-white/10">
                <div className="font-semibold text-lg mb-1 capitalize">{sourceName}</div>
                <div className="text-2xl font-bold text-cyan-400 mb-1">
                  {sourceData.count || 0} <span className="text-sm text-white/50">tools</span>
                </div>
                {sourceData.error && (
                  <div className="text-xs text-red-400 mt-2">⚠️ {sourceData.error.substring(0, 50)}</div>
                )}
                {sourceData.topics_scanned && (
                  <div className="text-xs text-white/50 mt-2">
                    {sourceData.topics_scanned} topics scanned
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// ==================== MARKETING AUTOMATION TAB ====================
const MarketingTab = ({ token }) => {
  const { data: campaigns } = useQuery({
    queryKey: ["marketing-campaigns"],
    queryFn: () => axios.get(`${API}/marketing/campaigns`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.data),
    refetchInterval: 30000
  });
  
  const { data: seoData } = useQuery({
    queryKey: ["seo-performance"],
    queryFn: () => axios.get(`${API}/marketing/seo`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.data),
  });
  
  return (
    <div className="space-y-6">
      {/* Marketing Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass rounded-xl p-4">
          <div className="text-3xl font-bold text-green-400">
            {campaigns?.campaigns?.length || 0}
          </div>
          <div className="text-sm text-white/60 mt-1">Active Campaigns</div>
        </div>
        <div className="glass rounded-xl p-4">
          <div className="text-3xl font-bold text-blue-400">
            {seoData?.organic_traffic?.last_30_days?.toLocaleString() || '0'}
          </div>
          <div className="text-sm text-white/60 mt-1">Organic Traffic</div>
        </div>
        <div className="glass rounded-xl p-4">
          <div className="text-3xl font-bold text-purple-400">
            {seoData?.backlinks?.total || 0}
          </div>
          <div className="text-sm text-white/60 mt-1">Backlinks</div>
        </div>
        <div className="glass rounded-xl p-4">
          <div className="text-3xl font-bold text-orange-400">
            {seoData?.keyword_rankings?.length || 0}
          </div>
          <div className="text-sm text-white/60 mt-1">Keywords Tracked</div>
        </div>
      </div>
      
      {/* SEO Performance */}
      {seoData && (
        <div className="glass rounded-xl p-6">
          <h3 className="font-rajdhani text-xl font-bold mb-4">📈 SEO Performance</h3>
          <div className="space-y-3">
            {seoData.keyword_rankings?.map((kw, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-white/5">
                <div>
                  <div className="font-semibold">{kw.keyword}</div>
                  <div className="text-xs text-white/50">{kw.volume?.toLocaleString()} searches/mo</div>
                </div>
                <div className={`text-lg font-bold ${kw.position <= 10 ? 'text-green-400' : kw.position <= 20 ? 'text-yellow-400' : 'text-white/50'}`}>
                  #{kw.position}
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-4 p-4 rounded-lg bg-cyan-500/10 border border-cyan-500/30">
            <div className="text-sm text-cyan-400 mb-2">Traffic Growth</div>
            <div className="text-2xl font-bold text-white">
              {seoData.organic_traffic?.growth || '+0%'}
            </div>
          </div>
        </div>
      )}
      
      {/* Campaigns List */}
      <div className="glass rounded-xl p-6">
        <h3 className="font-rajdhani text-xl font-bold mb-4">📢 Marketing Campaigns</h3>
        {campaigns?.campaigns && campaigns.campaigns.length > 0 ? (
          <div className="space-y-3">
            {campaigns.campaigns.slice(0, 10).map((campaign) => (
              <div key={campaign.id} className="p-4 rounded-lg bg-white/5 border border-white/10">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="font-semibold">{campaign.product_name}</div>
                    <div className="text-xs text-white/50 mt-1">
                      {new Date(campaign.created_at).toLocaleDateString()}
                    </div>
                  </div>
                  <div className="px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-xs font-semibold">
                    {campaign.status}
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 text-xs">
                  <div>
                    <div className="text-white/50">Impressions</div>
                    <div className="font-bold text-cyan-400">{campaign.performance?.impressions?.toLocaleString()}</div>
                  </div>
                  <div>
                    <div className="text-white/50">Conversions</div>
                    <div className="font-bold text-green-400">{campaign.performance?.conversions}</div>
                  </div>
                  <div>
                    <div className="text-white/50">CTR</div>
                    <div className="font-bold text-blue-400">{campaign.performance?.ctr}</div>
                  </div>
                  <div>
                    <div className="text-white/50">Conv. Rate</div>
                    <div className="font-bold text-purple-400">{campaign.performance?.conversion_rate}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-white/50">
            <div className="text-4xl mb-3">📢</div>
            <div>No campaigns yet. Create your first automated campaign!</div>
          </div>
        )}
      </div>
    </div>
  );
};


// ==================== MCP SERVERS TAB ====================
const MCPServersTab = ({ token }) => {
  const { data: mcpStatus } = useQuery({
    queryKey: ["mcp-status"],
    queryFn: () => axios.get(`${API}/admin/mcp/status`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.data),
    refetchInterval: 30000
  });
  
  const discoveredCount = mcpStatus?.discovered_servers || 0;
  const activeCount = mcpStatus?.active_connections || 0;
  const availableServers = mcpStatus?.available_servers || [];
  
  return (
    <div className="space-y-6">
      {/* MCP Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div className="glass rounded-xl p-4">
          <div className="text-3xl font-bold text-purple-400">{discoveredCount}</div>
          <div className="text-sm text-white/60 mt-1">MCP Servers Discovered</div>
        </div>
        <div className="glass rounded-xl p-4">
          <div className="text-3xl font-bold text-green-400">{activeCount}</div>
          <div className="text-sm text-white/60 mt-1">Active Connections</div>
        </div>
        <div className="glass rounded-xl p-4">
          <div className="text-3xl font-bold text-cyan-400">Demo</div>
          <div className="text-sm text-white/60 mt-1">Status</div>
        </div>
      </div>
      
      {/* What is MCP? */}
      <div className="glass rounded-xl p-6">
        <h3 className="font-rajdhani text-xl font-bold mb-3 flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-purple-400" />
          Model Context Protocol (MCP)
        </h3>
        <p className="text-white/70 text-sm mb-4">
          MCP is an open standard that enables AI models to connect to external tools and data sources. 
          NEXUS discovers and can integrate with MCP servers to extend platform capabilities.
        </p>
        <div className="grid md:grid-cols-2 gap-3 text-sm">
          <div className="p-3 rounded-lg bg-purple-500/10 border border-purple-500/30">
            <div className="font-semibold text-purple-400 mb-1">📡 Discovery</div>
            <div className="text-white/60">Automatically finds MCP servers from GitHub</div>
          </div>
          <div className="p-3 rounded-lg bg-cyan-500/10 border border-cyan-500/30">
            <div className="font-semibold text-cyan-400 mb-1">🔗 Integration</div>
            <div className="text-white/60">Connects to servers via HTTP or stdio transport</div>
          </div>
        </div>
      </div>
      
      {/* Discovered MCP Servers */}
      <div className="glass rounded-xl p-6">
        <h3 className="font-rajdhani text-xl font-bold mb-4">🔍 Discovered MCP Servers</h3>
        {availableServers.length > 0 ? (
          <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
            {availableServers.map((server, i) => (
              <div key={i} className="p-4 rounded-lg bg-white/5 border border-white/10 hover:border-purple-500/50 transition">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h4 className="font-semibold text-lg mb-1">{server.name}</h4>
                    <a 
                      href={server.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-sm text-cyan-400 hover:text-cyan-300 transition"
                    >
                      {server.url}
                    </a>
                    <div className="text-xs text-white/50 mt-2">Source: {server.source}</div>
                  </div>
                  <button 
                    className="px-4 py-2 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 text-purple-400 text-sm font-semibold transition"
                    onClick={() => toast.info("MCP connection in demo mode - full integration coming soon")}
                  >
                    Connect
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-white/50">
            <div className="text-4xl mb-3">🔌</div>
            <div>No MCP servers discovered yet</div>
            <div className="text-sm mt-2">Run a Mega Discovery scan to find MCP servers</div>
          </div>
        )}
      </div>
      
      {/* MCP Integration Status */}
      <div className="p-4 rounded-lg bg-purple-500/10 border border-purple-500/30">
        <div className="text-sm text-purple-400">
          <Sparkles className="w-4 h-4 inline mr-2" />
          {mcpStatus?.message || "MCP integration ready - discover servers via Mega Discovery"}
        </div>
      </div>
    </div>
  );
};


// ==================== CLOUDFLARE WORKERS TAB ====================
const CloudflareTab = ({ token }) => {
  const { data: workers } = useQuery({
    queryKey: ["cloudflare-workers"],
    queryFn: () => axios.get(`${API}/admin/cloudflare/workers`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.data),
    refetchInterval: 30000
  });
  
  return (
    <div className="space-y-6">
      {/* Workers Stats */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div className="glass rounded-xl p-4">
          <div className="text-3xl font-bold text-blue-400">
            {workers?.workers?.length || 0}
          </div>
          <div className="text-sm text-white/60 mt-1">Active Workers</div>
        </div>
        <div className="glass rounded-xl p-4">
          <div className="text-3xl font-bold text-green-400">Edge</div>
          <div className="text-sm text-white/60 mt-1">Computing</div>
        </div>
        <div className="glass rounded-xl p-4">
          <div className="text-3xl font-bold text-orange-400">Demo</div>
          <div className="text-sm text-white/60 mt-1">Status</div>
        </div>
      </div>
      
      {/* Workers List */}
      <div className="glass rounded-xl p-6">
        <h3 className="font-rajdhani text-xl font-bold mb-4">☁️ Deployed Edge Workers</h3>
        {workers?.workers && workers.workers.length > 0 ? (
          <div className="space-y-3">
            {workers.workers.map((worker, i) => (
              <div key={i} className="p-4 rounded-lg bg-white/5 border border-white/10">
                <div className="flex items-start justify-between mb-2">
                  <div className="font-semibold">{worker.name}</div>
                  <div className="px-3 py-1 rounded-full bg-yellow-500/20 text-yellow-400 text-xs font-semibold">
                    {worker.status}
                  </div>
                </div>
                {worker.routes && (
                  <div className="text-xs text-white/50">
                    Routes: {worker.routes.join(", ")}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-white/50">
            <div className="text-4xl mb-3">☁️</div>
            <div>Configure Cloudflare API to deploy edge workers</div>
          </div>
        )}
      </div>
      
      <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
        <div className="text-sm text-blue-400">
          <Sparkles className="w-4 h-4 inline mr-2" />
          Cloudflare Workers provide edge computing for image optimization, API caching, and real-time analytics
        </div>
      </div>
    </div>
  );
};

const getIntegrationIcon = (key) => {
  const icons = {
    emergent_llm: "🤖",
    stripe: "💳",
    resend: "📧",
    github: "🐙",
    gitlab: "🦊",
    producthunt: "🚀",
    manus: "🔮",
    softr: "🗄️"
  };
  return icons[key] || "🔧";
};


export default AutomationPanel;