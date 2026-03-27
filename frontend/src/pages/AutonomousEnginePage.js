import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import axios from "axios";
import {
  Bot, Sparkles, TrendingUp, GitBranch, Package, Activity,
  Play, Pause, RefreshCw, Search, Star, Clock, CheckCircle,
  AlertCircle, Loader2, ExternalLink, Code, Zap
} from "lucide-react";
import { useAuth, API } from "../App";

export const AutonomousEnginePage = () => {
  const { token } = useAuth();
  const [status, setStatus] = useState(null);
  const [integrations, setIntegrations] = useState([]);
  const [queue, setQueue] = useState([]);
  const [discovered, setDiscovered] = useState([]);
  const [loading, setLoading] = useState(true);
  const [discovering, setDiscovering] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    loadEngineStatus();
    loadIntegrations();
    loadQueue();
  }, []);

  const loadEngineStatus = async () => {
    try {
      const res = await axios.get(`${API}/api/autonomous/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStatus(res.data);
    } catch (err) {
      toast.error("Failed to load engine status");
    } finally {
      setLoading(false);
    }
  };

  const loadIntegrations = async () => {
    try {
      const res = await axios.get(`${API}/api/autonomous/integrations`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setIntegrations(Object.entries(res.data.integrations || {}));
    } catch (err) {
      console.error(err);
    }
  };

  const loadQueue = async () => {
    try {
      const res = await axios.get(`${API}/api/autonomous/queue`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setQueue(res.data.queue || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDiscover = async () => {
    setDiscovering(true);
    try {
      const res = await axios.post(
        `${API}/api/autonomous/discover`,
        { limit: 50 },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setDiscovered(res.data.integrations || []);
      toast.success(`Discovered ${res.data.discovered_count} integrations from ${res.data.sources.length} sources`);
    } catch (err) {
      toast.error("Discovery failed");
    } finally {
      setDiscovering(false);
    }
  };

  const handleStartLoop = async () => {
    try {
      const res = await axios.post(
        `${API}/api/autonomous/start-loop`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success("Continuous improvement loop started");
    } catch (err) {
      toast.error("Failed to start loop");
    }
  };

  const handleAutoUpdate = async (integrationName) => {
    try {
      const res = await axios.post(
        `${API}/api/autonomous/auto-update/${integrationName}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (res.data.success) {
        toast.success(`${integrationName} updated`);
        loadIntegrations();
      } else {
        toast.info("No updates available");
      }
    } catch (err) {
      toast.error("Update failed");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <Loader2 className="w-12 h-12 animate-spin text-purple-400" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Header */}
      <div className="border-b border-white/10 bg-black/20 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl">
                <Bot className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                  Autonomous Integration Engine
                </h1>
                <p className="text-gray-400 mt-1">Self-improving platform · Continuous discovery</p>
              </div>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleDiscover}
                disabled={discovering}
                className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-xl font-medium flex items-center gap-2 transition-all disabled:opacity-50"
              >
                {discovering ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
                Discover Now
              </button>
              <button
                onClick={handleStartLoop}
                className="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 rounded-xl font-medium flex items-center gap-2 transition-all"
              >
                <Play className="w-5 h-5" />
                Start Continuous Loop
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatCard
            icon={Package}
            label="Active Integrations"
            value={status?.integrations_count || 0}
            color="purple"
          />
          <StatCard
            icon={GitBranch}
            label="Discovery Sources"
            value={status?.discovery_sources || 0}
            color="blue"
          />
          <StatCard
            icon={Clock}
            label="Queue Size"
            value={status?.queue_size || 0}
            color="yellow"
          />
          <StatCard
            icon={Activity}
            label="Performance Score"
            value={status?.performance_score?.toFixed(1) || "N/A"}
            color="green"
          />
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-white/10">
          {["overview", "integrations", "discovered", "queue"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 font-medium capitalize transition-all ${
                activeTab === tab
                  ? "text-purple-400 border-b-2 border-purple-400"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Content */}
        {activeTab === "overview" && (
          <div className="space-y-6">
            <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Sparkles className="w-6 h-6 text-yellow-400" />
                How It Works
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <ProcessStep
                  number="1"
                  title="Discover"
                  description="Scans GitHub, PyPI, NPM, Product Hunt, Hacker News, and Reddit for new integrations"
                />
                <ProcessStep
                  number="2"
                  title="Evaluate"
                  description="Scores integrations on code quality, security, performance, and compatibility"
                />
                <ProcessStep
                  number="3"
                  title="Integrate"
                  description="Generates hybrid integrations combining best features and auto-deploys"
                />
              </div>
            </div>

            <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6">
              <h3 className="text-xl font-bold mb-4">Recommendation</h3>
              <p className="text-gray-300">{status?.recommendation || "Keep discovering new integrations to stay ahead!"}</p>
            </div>
          </div>
        )}

        {activeTab === "integrations" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {integrations.map(([name, data]) => (
              <IntegrationCard
                key={name}
                name={name}
                data={data}
                onUpdate={handleAutoUpdate}
              />
            ))}
          </div>
        )}

        {activeTab === "discovered" && (
          <div className="space-y-4">
            {discovered.length === 0 ? (
              <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-12 text-center">
                <Search className="w-16 h-16 mx-auto mb-4 text-gray-500" />
                <p className="text-gray-400 mb-4">No discoveries yet. Click "Discover Now" to find new integrations.</p>
              </div>
            ) : (
              discovered.map((integration, idx) => (
                <DiscoveredIntegrationCard key={idx} integration={integration} />
              ))
            )}
          </div>
        )}

        {activeTab === "queue" && (
          <div className="space-y-4">
            {queue.length === 0 ? (
              <div className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-12 text-center">
                <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-500" />
                <p className="text-gray-400">Queue is empty. All integrations processed!</p>
              </div>
            ) : (
              queue.map((item, idx) => (
                <QueueItem key={idx} item={item} index={idx} />
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

const StatCard = ({ icon: Icon, label, value, color }) => {
  const colors = {
    purple: "from-purple-500/20 to-pink-500/20 border-purple-500/30",
    blue: "from-blue-500/20 to-cyan-500/20 border-blue-500/30",
    yellow: "from-yellow-500/20 to-orange-500/20 border-yellow-500/30",
    green: "from-green-500/20 to-emerald-500/20 border-green-500/30"
  };

  return (
    <div className={`bg-gradient-to-br ${colors[color]} backdrop-blur-xl rounded-2xl border p-6`}>
      <Icon className="w-8 h-8 mb-3 opacity-80" />
      <div className="text-3xl font-bold mb-1">{value}</div>
      <div className="text-sm text-gray-400">{label}</div>
    </div>
  );
};

const ProcessStep = ({ number, title, description }) => (
  <div className="bg-white/5 rounded-xl p-4 border border-white/10">
    <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center font-bold mb-3">
      {number}
    </div>
    <h4 className="font-bold mb-2">{title}</h4>
    <p className="text-sm text-gray-400">{description}</p>
  </div>
);

const IntegrationCard = ({ name, data, onUpdate }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6 hover:border-purple-500/50 transition-all"
  >
    <div className="flex items-start justify-between mb-4">
      <div>
        <h3 className="text-xl font-bold capitalize">{name.replace(/_/g, " ")}</h3>
        <p className="text-sm text-gray-400 mt-1">{data.type}</p>
      </div>
      <div className="flex items-center gap-2 px-3 py-1 bg-green-500/20 rounded-full text-green-400 text-sm">
        <Star className="w-4 h-4" />
        {data.performance}
      </div>
    </div>
    
    <div className="space-y-2 mb-4">
      <div className="text-sm">
        <span className="text-gray-400">Technologies:</span>{" "}
        <span className="text-white">{data.technologies?.join(", ")}</span>
      </div>
      <div className="text-sm">
        <span className="text-gray-400">Version:</span>{" "}
        <span className="text-white">{data.version}</span>
      </div>
    </div>

    <button
      onClick={() => onUpdate(name)}
      className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-all"
    >
      <RefreshCw className="w-4 h-4" />
      Check for Updates
    </button>
  </motion.div>
);

const DiscoveredIntegrationCard = ({ integration }) => (
  <div className="bg-white/5 backdrop-blur-xl rounded-xl border border-white/10 p-6 hover:border-purple-500/50 transition-all">
    <div className="flex items-start justify-between">
      <div className="flex-1">
        <div className="flex items-center gap-3 mb-2">
          <h3 className="text-lg font-bold">{integration.name}</h3>
          <span className="px-2 py-1 bg-blue-500/20 rounded text-xs text-blue-400">
            {integration.source}
          </span>
        </div>
        <p className="text-sm text-gray-400 mb-3">{integration.description}</p>
        <div className="flex gap-4 text-sm">
          {integration.stars && (
            <div className="flex items-center gap-1 text-yellow-400">
              <Star className="w-4 h-4" />
              {integration.stars}
            </div>
          )}
          {integration.language && (
            <div className="flex items-center gap-1 text-gray-400">
              <Code className="w-4 h-4" />
              {integration.language}
            </div>
          )}
          {integration.score && (
            <div className="flex items-center gap-1 text-green-400">
              <Zap className="w-4 h-4" />
              Score: {integration.score.toFixed(1)}
            </div>
          )}
        </div>
      </div>
      {integration.url && (
        <a
          href={integration.url}
          target="_blank"
          rel="noopener noreferrer"
          className="p-2 hover:bg-white/10 rounded-lg transition-all"
        >
          <ExternalLink className="w-5 h-5" />
        </a>
      )}
    </div>
  </div>
);

const QueueItem = ({ item, index }) => (
  <div className="bg-white/5 backdrop-blur-xl rounded-xl border border-white/10 p-4 flex items-center gap-4">
    <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center font-bold text-sm">
      {index + 1}
    </div>
    <div className="flex-1">
      <h4 className="font-bold">{item.name}</h4>
      <p className="text-sm text-gray-400">{item.source || "Pending integration"}</p>
    </div>
    <AlertCircle className="w-5 h-5 text-yellow-400" />
  </div>
);
