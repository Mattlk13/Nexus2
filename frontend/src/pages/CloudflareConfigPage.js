import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { motion } from "framer-motion";
import { toast } from "sonner";
import {
  Cloud, Key, CheckCircle, AlertCircle, Loader2, ExternalLink,
  Database, Zap, Shield, Search, Code, Server, Lock
} from "lucide-react";
import { useAuth, API } from "../App";

export const CloudflareConfigPage = () => {
  const { user, token } = useAuth();
  const queryClient = useQueryClient();
  const [accountId, setAccountId] = useState("");
  const [apiToken, setApiToken] = useState("");
  const [zoneId, setZoneId] = useState("");
  const [showToken, setShowToken] = useState(false);

  // Get Cloudflare status
  const { data: status, isLoading } = useQuery({
    queryKey: ["cloudflare-status"],
    queryFn: () => axios.get(`${API}/admin/cloudflare/status`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.data),
    enabled: !!token && user?.role === "admin"
  });

  // Configure Cloudflare
  const configureMutation = useMutation({
    mutationFn: (config) => axios.post(`${API}/admin/cloudflare/configure`, config, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.data),
    onSuccess: (data) => {
      toast.success(`Cloudflare configured: ${data.account}`);
      queryClient.invalidateQueries(["cloudflare-status"]);
      setApiToken(""); // Clear for security
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || "Configuration failed");
    }
  });

  // Initialize all services
  const initializeMutation = useMutation({
    mutationFn: () => axios.post(`${API}/admin/cloudflare/initialize`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.data),
    onSuccess: (data) => {
      toast.success("All Cloudflare services initialized!");
      queryClient.invalidateQueries(["cloudflare-status"]);
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || "Initialization failed");
    }
  });

  const handleConfigure = () => {
    if (!accountId || !apiToken) {
      toast.error("Account ID and API Token are required");
      return;
    }

    configureMutation.mutate({
      account_id: accountId,
      api_token: apiToken,
      zone_id: zoneId
    });
  };

  const handleInitialize = () => {
    if (!status?.configured) {
      toast.error("Please configure Cloudflare credentials first");
      return;
    }
    initializeMutation.mutate();
  };

  if (user?.role !== "admin") {
    return (
      <div className="min-h-screen pt-28 flex items-center justify-center">
        <p className="text-white/60">Admin access required</p>
      </div>
    );
  }

  const isConfigured = status?.configured;
  const features = status?.features || {};

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="font-rajdhani text-4xl font-bold mb-2">
            <span className="gradient-text">Cloudflare Integration</span>
          </h1>
          <p className="text-white/60">Configure and manage all Cloudflare services for NEXUS</p>
        </div>

        {/* Status Card */}
        {isConfigured && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass rounded-xl p-6 mb-8"
          >
            <div className="flex items-center gap-3 mb-4">
              <CheckCircle className="w-8 h-8 text-green-400" />
              <div>
                <h2 className="font-rajdhani text-xl font-bold">Cloudflare Connected</h2>
                <p className="text-sm text-white/60">Account ID: {status.account_id?.slice(0, 16)}...</p>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {Object.entries(features).map(([key, config]) => (
                <div key={key} className="p-4 rounded-lg bg-white/5">
                  <div className="flex items-center gap-2 mb-2">
                    {config.enabled ? (
                      <CheckCircle className="w-4 h-4 text-green-400" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-white/40" />
                    )}
                    <span className="text-sm font-semibold uppercase">{key.replace('_', ' ')}</span>
                  </div>
                  <p className="text-xs text-white/60">
                    {config.enabled ? "Active" : "Not initialized"}
                  </p>
                </div>
              ))}
            </div>

            <button
              onClick={handleInitialize}
              disabled={initializeMutation.isPending}
              className="mt-6 btn-primary px-6 py-3 rounded-lg flex items-center gap-2"
            >
              {initializeMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Zap className="w-4 h-4" />
              )}
              Initialize All Services
            </button>
          </motion.div>
        )}

        {/* Configuration Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass rounded-xl p-6 mb-8"
        >
          <h2 className="font-rajdhani text-2xl font-bold mb-4">
            {isConfigured ? "Update Configuration" : "Configure Cloudflare"}
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Account ID *</label>
              <input
                type="text"
                value={accountId}
                onChange={(e) => setAccountId(e.target.value)}
                placeholder="9ea3a006589428efed0480da5c037163"
                className="w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 focus:border-cyan-500 focus:outline-none"
              />
              <p className="text-xs text-white/40 mt-1">
                Found in: Dashboard → Any domain → Right sidebar "Account ID"
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">API Token *</label>
              <div className="relative">
                <input
                  type={showToken ? "text" : "password"}
                  value={apiToken}
                  onChange={(e) => setApiToken(e.target.value)}
                  placeholder="Enter your Cloudflare API token"
                  className="w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 focus:border-cyan-500 focus:outline-none"
                />
                <button
                  onClick={() => setShowToken(!showToken)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white"
                >
                  {showToken ? <Lock className="w-4 h-4" /> : <Key className="w-4 h-4" />}
                </button>
              </div>
              <p className="text-xs text-white/40 mt-1">
                Create at: <a href="https://dash.cloudflare.com/profile/api-tokens" target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:underline">dash.cloudflare.com/profile/api-tokens</a>
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Zone ID (Optional)</label>
              <input
                type="text"
                value={zoneId}
                onChange={(e) => setZoneId(e.target.value)}
                placeholder="Only if you have a domain on Cloudflare"
                className="w-full px-4 py-3 rounded-lg bg-white/10 border border-white/20 focus:border-cyan-500 focus:outline-none"
              />
            </div>

            <button
              onClick={handleConfigure}
              disabled={configureMutation.isPending}
              className="w-full btn-primary py-4 rounded-xl flex items-center justify-center gap-2"
            >
              {configureMutation.isPending ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Cloud className="w-5 h-5" />
              )}
              {isConfigured ? "Update Configuration" : "Configure Cloudflare"}
            </button>
          </div>
        </motion.div>

        {/* Setup Guide */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass rounded-xl p-6"
        >
          <h3 className="font-rajdhani text-xl font-bold mb-4">📘 How to Get Your API Token</h3>
          
          <div className="space-y-4">
            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-cyan-500 flex items-center justify-center flex-shrink-0 font-bold">
                1
              </div>
              <div>
                <p className="font-semibold mb-1">Log in to Cloudflare</p>
                <p className="text-sm text-white/60">
                  Email: hm2krebsmatthewl@gmail.com<br />
                  Go to: <a href="https://dash.cloudflare.com" target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:underline inline-flex items-center gap-1">
                    dash.cloudflare.com <ExternalLink className="w-3 h-3" />
                  </a>
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-cyan-500 flex items-center justify-center flex-shrink-0 font-bold">
                2
              </div>
              <div>
                <p className="font-semibold mb-1">Create API Token</p>
                <p className="text-sm text-white/60">
                  Profile → API Tokens → "Create Token"<br />
                  Use template: <strong>"Edit Cloudflare Workers"</strong>
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-cyan-500 flex items-center justify-center flex-shrink-0 font-bold">
                3
              </div>
              <div>
                <p className="font-semibold mb-1">Add Permissions</p>
                <p className="text-sm text-white/60">
                  • Workers Scripts: Edit<br />
                  • Workers KV: Edit<br />
                  • Workers R2: Edit<br />
                  • D1: Edit
                </p>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-cyan-500 flex items-center justify-center flex-shrink-0 font-bold">
                4
              </div>
              <div>
                <p className="font-semibold mb-1">Copy & Paste</p>
                <p className="text-sm text-white/60">
                  Copy the generated token and paste it above
                </p>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Services Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-8 glass rounded-xl p-6"
        >
          <h3 className="font-rajdhani text-xl font-bold mb-4">🚀 Services That Will Be Enabled</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { icon: Database, name: "Workers KV", desc: "Edge caching for 10-100x faster reads" },
              { icon: Server, name: "R2 Storage", desc: "Zero-egress file storage" },
              { icon: Zap, name: "Workers AI", desc: "Serverless AI inference (90% cheaper)" },
              { icon: Shield, name: "Turnstile", desc: "Bot protection (free, unlimited)" },
              { icon: Search, name: "Vectorize", desc: "Semantic search & recommendations" },
              { icon: Code, name: "D1 Database", desc: "Serverless SQL at the edge" }
            ].map((service, idx) => (
              <div key={idx} className="flex gap-3 p-4 rounded-lg bg-white/5">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center flex-shrink-0">
                  <service.icon className="w-5 h-5 text-white" />
                </div>
                <div>
                  <p className="font-semibold mb-1">{service.name}</p>
                  <p className="text-sm text-white/60">{service.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};
