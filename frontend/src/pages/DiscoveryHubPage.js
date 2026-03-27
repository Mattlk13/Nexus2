import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import {
  Server, Workflow, Search, Filter, ExternalLink, Star, 
  Zap, Database, Package, Code, Cloud, Lock, Loader2,
  CheckCircle, TrendingUp, Award, GitBranch
} from "lucide-react";
import { useAuth, API } from "../App";

export const DiscoveryHubPage = () => {
  const { token, user } = useAuth();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState("mcp");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");

  // Fetch MCP Servers
  const { data: mcpData, isLoading: mcpLoading } = useQuery({
    queryKey: ["mcp-registry"],
    queryFn: () => axios.get(`${API}/mcp/registry`).then(r => r.data)
  });

  // Fetch Workflow Tools
  const { data: workflowData, isLoading: workflowLoading } = useQuery({
    queryKey: ["workflow-tools"],
    queryFn: () => axios.get(`${API}/workflow-tools`).then(r => r.data)
  });

  // Trigger MCP Discovery
  const discoverMCP = useMutation({
    mutationFn: () => axios.post(`${API}/mcp/registry/discover`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.data),
    onSuccess: (data) => {
      toast.success(`Discovered ${data.total_discovered} MCP servers!`);
      queryClient.invalidateQueries(["mcp-registry"]);
    },
    onError: () => toast.error("Failed to discover MCP servers")
  });

  // Trigger Workflow Cataloging
  const catalogWorkflow = useMutation({
    mutationFn: () => axios.post(`${API}/workflow-tools/catalog`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.data),
    onSuccess: (data) => {
      toast.success(`Cataloged ${data.total_cataloged} workflow tools!`);
      queryClient.invalidateQueries(["workflow-tools"]);
    },
    onError: () => toast.error("Failed to catalog workflow tools")
  });

  const mcpServers = mcpData?.servers || [];
  const workflowTools = workflowData?.tools || [];

  // Filter logic
  const filterItems = (items, type) => {
    return items.filter(item => {
      const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           item.description.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCategory = selectedCategory === "all" || item.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  };

  const filteredMCP = filterItems(mcpServers, "mcp");
  const filteredWorkflow = filterItems(workflowTools, "workflow");

  const categoryColors = {
    "Development": "cyan",
    "Database": "purple",
    "Payments": "green",
    "Productivity": "blue",
    "Automation": "orange",
    "Workflow Automation": "pink",
    "AI Prototyping": "yellow",
    "Team Collaboration": "indigo"
  };

  const priorityColors = {
    "critical": "red",
    "high": "orange",
    "medium": "blue",
    "low": "gray"
  };

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="font-rajdhani text-4xl font-bold mb-2">
            <span className="gradient-text">Discovery Hub</span>
          </h1>
          <p className="text-white/60">Explore MCP servers and AI workflow automation tools</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-8">
          <button
            onClick={() => setActiveTab("mcp")}
            className={`px-6 py-3 rounded-lg font-semibold transition-all flex items-center gap-2 ${
              activeTab === "mcp" 
                ? "bg-cyan-500 text-white" 
                : "bg-white/10 text-white/60 hover:bg-white/20"
            }`}
          >
            <Server className="w-5 h-5" />
            MCP Servers ({mcpServers.length})
          </button>
          <button
            onClick={() => setActiveTab("workflow")}
            className={`px-6 py-3 rounded-lg font-semibold transition-all flex items-center gap-2 ${
              activeTab === "workflow" 
                ? "bg-purple-500 text-white" 
                : "bg-white/10 text-white/60 hover:bg-white/20"
            }`}
          >
            <Workflow className="w-5 h-5" />
            Workflow Tools ({workflowTools.length})
          </button>
        </div>

        {/* Search & Actions */}
        <div className="glass rounded-xl p-4 mb-8 flex gap-4 items-center">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/40" />
            <input
              type="text"
              placeholder={`Search ${activeTab === "mcp" ? "MCP servers" : "workflow tools"}...`}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-cyan-500 focus:outline-none"
            />
          </div>
          
          {user?.role === "admin" && (
            <button
              onClick={() => activeTab === "mcp" ? discoverMCP.mutate() : catalogWorkflow.mutate()}
              disabled={discoverMCP.isPending || catalogWorkflow.isPending}
              className="btn-primary px-6 py-3 rounded-lg flex items-center gap-2 whitespace-nowrap"
            >
              {discoverMCP.isPending || catalogWorkflow.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <TrendingUp className="w-4 h-4" />
              )}
              {activeTab === "mcp" ? "Discover MCP" : "Catalog Tools"}
            </button>
          )}
        </div>

        {/* MCP Servers Tab */}
        {activeTab === "mcp" && (
          <div>
            {mcpLoading ? (
              <div className="flex items-center justify-center py-20">
                <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <AnimatePresence>
                  {filteredMCP.map((server, idx) => (
                    <motion.div
                      key={server.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, scale: 0.9 }}
                      transition={{ delay: idx * 0.05 }}
                      className="glass rounded-xl p-6 hover:bg-white/10 transition-all"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br from-${categoryColors[server.category] || 'cyan'}-500 to-${categoryColors[server.category] || 'purple'}-600 flex items-center justify-center`}>
                          <Server className="w-6 h-6 text-white" />
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold bg-${priorityColors[server.priority]}-500/20 text-${priorityColors[server.priority]}-400`}>
                          {server.priority}
                        </span>
                      </div>

                      <h3 className="font-rajdhani text-xl font-bold mb-2">{server.name}</h3>
                      <p className="text-sm text-white/60 mb-4 line-clamp-2">{server.description}</p>

                      <div className="mb-4">
                        <span className="px-3 py-1 rounded-full bg-white/10 text-xs">{server.category}</span>
                      </div>

                      <div className="mb-4">
                        <p className="text-xs text-white/40 mb-2">Capabilities:</p>
                        <div className="flex flex-wrap gap-1">
                          {server.capabilities?.slice(0, 3).map((cap, i) => (
                            <span key={i} className="px-2 py-1 rounded bg-cyan-500/20 text-cyan-400 text-xs">
                              {cap}
                            </span>
                          ))}
                        </div>
                      </div>

                      <a
                        href={server.github_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-cyan-400 hover:text-cyan-300 text-sm"
                      >
                        <ExternalLink className="w-4 h-4" />
                        View on GitHub
                      </a>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            )}
          </div>
        )}

        {/* Workflow Tools Tab */}
        {activeTab === "workflow" && (
          <div>
            {workflowLoading ? (
              <div className="flex items-center justify-center py-20">
                <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <AnimatePresence>
                  {filteredWorkflow.map((tool, idx) => (
                    <motion.div
                      key={tool.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, scale: 0.9 }}
                      transition={{ delay: idx * 0.05 }}
                      className="glass rounded-xl p-6 hover:bg-white/10 transition-all"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <div className="flex items-center gap-3 mb-2">
                            <h3 className="font-rajdhani text-2xl font-bold">{tool.name}</h3>
                            <div className="flex items-center gap-1 px-2 py-1 rounded bg-yellow-500/20">
                              <Star className="w-3 h-3 text-yellow-400" />
                              <span className="text-yellow-400 text-xs font-semibold">{tool.rating}</span>
                            </div>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold bg-${priorityColors[tool.priority]}-500/20 text-${priorityColors[tool.priority]}-400`}>
                            {tool.priority}
                          </span>
                        </div>
                      </div>

                      <p className="text-white/70 mb-4">{tool.description}</p>

                      <div className="mb-4 p-3 rounded-lg bg-white/5">
                        <p className="text-sm text-white/60 mb-1">Best for:</p>
                        <p className="text-sm">{tool.use_case}</p>
                      </div>

                      <div className="mb-4">
                        <p className="text-xs text-white/40 mb-2">Key Features:</p>
                        <div className="flex flex-wrap gap-2">
                          {tool.features?.map((feat, i) => (
                            <span key={i} className="px-2 py-1 rounded bg-purple-500/20 text-purple-400 text-xs">
                              {feat}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="flex items-center justify-between pt-4 border-t border-white/10">
                        <div>
                          <p className="text-xs text-white/40">Pricing</p>
                          <p className="text-sm font-semibold">{tool.pricing}</p>
                        </div>
                        <a
                          href={tool.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn-primary px-4 py-2 rounded-lg flex items-center gap-2 text-sm"
                        >
                          <ExternalLink className="w-4 h-4" />
                          Visit
                        </a>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
