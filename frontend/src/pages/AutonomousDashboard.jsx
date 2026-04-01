import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useAuth } from "../App";
import { API } from "../config";
import axios from "axios";
import {
  Activity, Cpu, Database, Zap, Shield, GitBranch, Bot,
  CheckCircle, AlertTriangle, XCircle, TrendingUp, TrendingDown,
  Play, Pause, RefreshCw, Settings, BarChart3, Server
} from "lucide-react";

const AutonomousDashboard = () => {
  const { user, token } = useAuth();
  const [autonomousStatus, setAutonomousStatus] = useState("inactive");
  const [agents, setAgents] = useState([]);
  const [systemHealth, setSystemHealth] = useState({});
  const [metrics, setMetrics] = useState({});
  const [healingHistory, setHealingHistory] = useState([]);
  const [deployments, setDeployments] = useState([]);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 10000); // Refresh every 10s
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      // Load agents
      const agentsRes = await axios.get(`${API}/v2/hybrid/autonomous/agents`, { headers });
      setAgents(agentsRes.data.agents);
      
      // Load system health
      const healthRes = await axios.get(`${API}/v2/hybrid/selfhealing/health`, { headers });
      setSystemHealth(healthRes.data);
      
      // Load metrics
      const metricsRes = await axios.get(`${API}/v2/hybrid/selfhealing/metrics`, { headers });
      setMetrics(metricsRes.data);
      
      // Load healing history
      const healingRes = await axios.get(`${API}/v2/hybrid/selfhealing/healing-history`, { headers });
      setHealingHistory(healingRes.data.actions);
      
      // Load deployments
      const deploymentsRes = await axios.get(`${API}/v2/hybrid/cicd/deployments`, { headers });
      setDeployments(deploymentsRes.data.deployments);
      
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
    }
  };

  const startAutonomousMode = async () => {
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      await axios.post(`${API}/v2/hybrid/autonomous/start`, {}, { headers });
      await axios.post(`${API}/v2/hybrid/selfhealing/start`, {}, { headers });
      
      setAutonomousStatus("active");
      alert("✅ Autonomous mode activated!");
    } catch (err) {
      alert(`Error: ${err.response?.data?.detail || err.message}`);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case "healthy":
      case "active":
      case "success":
        return "text-green-400 bg-green-500/20";
      case "degraded":
      case "warning":
        return "text-yellow-400 bg-yellow-500/20";
      case "down":
      case "failed":
        return "text-red-400 bg-red-500/20";
      default:
        return "text-gray-400 bg-gray-500/20";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "healthy":
      case "active":
      case "success":
        return <CheckCircle className="w-5 h-5" />;
      case "degraded":
      case "warning":
        return <AlertTriangle className="w-5 h-5" />;
      case "down":
      case "failed":
        return <XCircle className="w-5 h-5" />;
      default:
        return <Activity className="w-5 h-5" />;
    }
  };

  return (
    <div className="min-h-screen pt-32 pb-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="font-rajdhani text-4xl font-bold mb-2">
                Autonomous Platform Control
              </h1>
              <p className="text-white/60">
                AI-powered platform management • {agents.length} agents active
              </p>
            </div>
            
            <button
              onClick={startAutonomousMode}
              disabled={autonomousStatus === "active"}
              className={`px-6 py-3 rounded-xl font-semibold flex items-center gap-2 ${
                autonomousStatus === "active"
                  ? "bg-green-500/20 text-green-400 border border-green-500/50"
                  : "bg-gradient-to-r from-cyan-500 to-purple-600 hover:shadow-lg"
              }`}
            >
              {autonomousStatus === "active" ? (
                <>
                  <CheckCircle className="w-5 h-5" />
                  Autonomous Mode Active
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Start Autonomous Mode
                </>
              )}
            </button>
          </div>
        </motion.div>

        {/* System Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="glass rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Cpu className="w-5 h-5 text-cyan-400" />
                <span className="text-sm font-medium">CPU Usage</span>
              </div>
              <span className="text-xl font-bold">{metrics.cpu_percent?.toFixed(1) || 0}%</span>
            </div>
            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-cyan-500 to-blue-500"
                style={{ width: `${metrics.cpu_percent || 0}%` }}
              />
            </div>
          </div>

          <div className="glass rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Server className="w-5 h-5 text-purple-400" />
                <span className="text-sm font-medium">Memory</span>
              </div>
              <span className="text-xl font-bold">{metrics.memory_percent?.toFixed(1) || 0}%</span>
            </div>
            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                style={{ width: `${metrics.memory_percent || 0}%` }}
              />
            </div>
          </div>

          <div className="glass rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-400" />
                <span className="text-sm font-medium">Response Time</span>
              </div>
              <span className="text-xl font-bold">{metrics.response_time?.toFixed(0) || 0}ms</span>
            </div>
            <div className="text-xs text-white/40">Average API response</div>
          </div>

          <div className="glass rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Shield className="w-5 h-5 text-green-400" />
                <span className="text-sm font-medium">Error Rate</span>
              </div>
              <span className="text-xl font-bold">{metrics.error_rate?.toFixed(1) || 0}%</span>
            </div>
            <div className="text-xs text-white/40">Last 1 hour</div>
          </div>
        </div>

        {/* Autonomous Agents */}
        <div className="glass rounded-2xl p-6 mb-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Bot className="w-6 h-6 text-cyan-400" />
            Autonomous Agents
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {agents.map((agent) => (
              <div key={agent.id} className="bg-white/5 rounded-xl p-4 border border-white/10">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-sm">{agent.name}</h3>
                  <div className={`px-2 py-1 rounded-md text-xs ${getStatusColor(agent.status)}`}>
                    {agent.status}
                  </div>
                </div>
                <div className="text-xs text-white/60 mb-2">
                  Role: {agent.role}
                </div>
                <div className="flex flex-wrap gap-1">
                  {agent.capabilities.slice(0, 3).map((cap, i) => (
                    <span key={i} className="text-xs px-2 py-1 bg-white/10 rounded-md">
                      {cap}
                    </span>
                  ))}
                  {agent.capabilities.length > 3 && (
                    <span className="text-xs px-2 py-1 bg-white/10 rounded-md">
                      +{agent.capabilities.length - 3}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* System Health */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="glass rounded-2xl p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Activity className="w-6 h-6 text-green-400" />
              System Health
            </h2>
            
            <div className="space-y-3">
              {Object.entries(systemHealth).map(([service, status]) => (
                <div key={service} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${getStatusColor(status.status)}`}>
                      {getStatusIcon(status.status)}
                    </div>
                    <div>
                      <div className="font-medium capitalize">{service}</div>
                      {status.error && (
                        <div className="text-xs text-red-400">{status.error}</div>
                      )}
                    </div>
                  </div>
                  <div className={`px-3 py-1 rounded-md text-xs ${getStatusColor(status.status)}`}>
                    {status.status}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="glass rounded-2xl p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <RefreshCw className="w-6 h-6 text-blue-400" />
              Recent Healing Actions
            </h2>
            
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {healingHistory.slice(0, 10).map((action, i) => (
                <div key={i} className="p-3 bg-white/5 rounded-lg text-sm">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium capitalize">{action.service}</span>
                    <span className="text-xs text-white/40">
                      {new Date(action.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="text-xs text-white/60">
                    Action: {action.action} • Status: {action.status.status}
                  </div>
                </div>
              ))}
              
              {healingHistory.length === 0 && (
                <div className="text-center text-white/40 py-8">
                  No healing actions yet
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Recent Deployments */}
        <div className="glass rounded-2xl p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <GitBranch className="w-6 h-6 text-purple-400" />
            Recent Deployments
          </h2>
          
          <div className="space-y-3">
            {deployments.slice(0, 5).map((deployment, i) => (
              <div key={i} className="p-4 bg-white/5 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${getStatusColor(deployment.status)}`}>
                      {getStatusIcon(deployment.status)}
                    </div>
                    <div>
                      <div className="font-medium">{deployment.id}</div>
                      <div className="text-xs text-white/60">
                        Trigger: {deployment.trigger}
                      </div>
                    </div>
                  </div>
                  <div className={`px-3 py-1 rounded-md text-xs ${getStatusColor(deployment.status)}`}>
                    {deployment.status}
                  </div>
                </div>
                
                {deployment.stages_completed && (
                  <div className="text-xs text-white/60">
                    Stages completed: {deployment.stages_completed.length}/10
                  </div>
                )}
              </div>
            ))}
            
            {deployments.length === 0 && (
              <div className="text-center text-white/40 py-8">
                No deployments yet
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutonomousDashboard;
