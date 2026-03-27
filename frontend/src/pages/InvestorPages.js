import React from "react";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import axios from "axios";
import { 
  TrendingUp, Users, DollarSign, Package, Award, 
  Building2, Mail, Globe, ArrowUpRight, Sparkles 
} from "lucide-react";
import { API, useAuth } from "../App";

// ==================== INVESTOR DASHBOARD PAGE ====================
export const InvestorDashboardPage = () => {
  const { token } = useAuth();
  
  const { data: dashboard, isLoading } = useQuery({
    queryKey: ["investor-dashboard"],
    queryFn: () => axios.get(`${API}/admin/investor-dashboard`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.data),
    enabled: !!token
  });
  
  const { data: pitchData } = useQuery({
    queryKey: ["pitch-deck-data"],
    queryFn: () => axios.get(`${API}/admin/pitch-deck-data`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.data),
    enabled: !!token
  });
  
  if (isLoading) {
    return (
      <div className="min-h-screen pt-20 pb-10 px-4 flex items-center justify-center">
        <div className="text-white/50">Loading investor dashboard...</div>
      </div>
    );
  }
  
  const metrics = dashboard?.platform_metrics || {};
  const growth = dashboard?.growth_metrics || {};
  const market = dashboard?.market_position || {};
  const investorDb = dashboard?.investor_database || {};
  const fundraising = dashboard?.fundraising_status || {};
  const keyMetrics = dashboard?.key_metrics || {};
  
  return (
    <div className="min-h-screen pt-20 pb-10 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="font-rajdhani text-4xl md:text-5xl font-bold mb-3 bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
            Investor Dashboard
          </h1>
          <p className="text-white/60">Comprehensive platform metrics and investor database</p>
        </motion.div>
        
        {/* Key Platform Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="glass rounded-xl p-6">
            <Users className="w-8 h-8 text-cyan-400 mb-3" />
            <div className="text-3xl font-bold text-white mb-1">
              {metrics.total_users?.toLocaleString()}
            </div>
            <div className="text-sm text-white/60">Total Users</div>
            <div className="text-xs text-green-400 mt-2">
              {growth.user_growth_30d} in 30d
            </div>
          </div>
          
          <div className="glass rounded-xl p-6">
            <Package className="w-8 h-8 text-purple-400 mb-3" />
            <div className="text-3xl font-bold text-white mb-1">
              {metrics.total_products?.toLocaleString()}
            </div>
            <div className="text-sm text-white/60">Products Listed</div>
            <div className="text-xs text-green-400 mt-2">
              {growth.product_growth_30d} in 30d
            </div>
          </div>
          
          <div className="glass rounded-xl p-6">
            <DollarSign className="w-8 h-8 text-green-400 mb-3" />
            <div className="text-3xl font-bold text-white mb-1">
              ${metrics.total_revenue?.toLocaleString()}
            </div>
            <div className="text-sm text-white/60">Total Revenue</div>
            <div className="text-xs text-green-400 mt-2">
              {growth.revenue_growth_30d} in 30d
            </div>
          </div>
          
          <div className="glass rounded-xl p-6">
            <Sparkles className="w-8 h-8 text-cyan-400 mb-3" />
            <div className="text-3xl font-bold text-white mb-1">
              {metrics.ai_agents_active}
            </div>
            <div className="text-sm text-white/60">AI Agents Active</div>
            <div className="text-xs text-cyan-400 mt-2">Autonomous</div>
          </div>
        </div>
        
        {/* Fundraising Status */}
        <div className="glass rounded-xl p-6 mb-8">
          <h2 className="font-rajdhani text-2xl font-bold mb-4 flex items-center gap-2">
            <Award className="w-6 h-6 text-yellow-400" />
            Fundraising Status
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <div className="text-sm text-white/60 mb-1">Current Stage</div>
              <div className="text-xl font-bold text-cyan-400">{fundraising.current_stage}</div>
            </div>
            <div>
              <div className="text-sm text-white/60 mb-1">Target Raise</div>
              <div className="text-xl font-bold text-green-400">{fundraising.target_raise}</div>
            </div>
            <div>
              <div className="text-sm text-white/60 mb-1">Valuation</div>
              <div className="text-xl font-bold text-purple-400">{fundraising.valuation}</div>
            </div>
          </div>
          
          <div className="mt-6 p-4 rounded-lg bg-cyan-500/10 border border-cyan-500/30">
            <div className="text-sm text-cyan-400 font-semibold mb-2">Use of Funds</div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
              {fundraising.use_of_funds && Object.entries(fundraising.use_of_funds).map(([key, val]) => (
                <div key={key}>
                  <div className="text-white/50 capitalize">{key.replace('_', ' ')}</div>
                  <div className="font-bold text-white">{val}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {/* Key SaaS Metrics */}
        <div className="glass rounded-xl p-6 mb-8">
          <h2 className="font-rajdhani text-2xl font-bold mb-4">📊 Key Metrics</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="p-4 rounded-lg bg-white/5">
              <div className="text-sm text-white/60 mb-1">LTV:CAC Ratio</div>
              <div className="text-2xl font-bold text-green-400">{keyMetrics.ltv_cac_ratio}</div>
            </div>
            <div className="p-4 rounded-lg bg-white/5">
              <div className="text-sm text-white/60 mb-1">Gross Margin</div>
              <div className="text-2xl font-bold text-cyan-400">{keyMetrics.gross_margin}</div>
            </div>
            <div className="p-4 rounded-lg bg-white/5">
              <div className="text-sm text-white/60 mb-1">NRR</div>
              <div className="text-2xl font-bold text-purple-400">{keyMetrics.net_revenue_retention}</div>
            </div>
          </div>
        </div>
        
        {/* Investor Database */}
        <div className="glass rounded-xl p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="font-rajdhani text-2xl font-bold flex items-center gap-2">
              <Building2 className="w-6 h-6 text-cyan-400" />
              Investor Database ({investorDb.total_investors})
            </h2>
            <div className="flex gap-2 text-sm">
              <span className="px-3 py-1 rounded-full bg-yellow-500/20 text-yellow-400">
                Tier 1: {investorDb.tier_1_funds}
              </span>
              <span className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-400">
                Tier 2: {investorDb.tier_2_funds}
              </span>
            </div>
          </div>
          
          <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
            {investorDb.investors?.slice(0, 30).map((investor, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.02 }}
                className="p-4 rounded-lg bg-white/5 border border-white/10 hover:border-cyan-500/50 transition"
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-lg">{investor.name}</h3>
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${
                        investor.tier === 1 ? 'bg-yellow-500/20 text-yellow-400' :
                        investor.tier === 2 ? 'bg-blue-500/20 text-blue-400' :
                        'bg-gray-500/20 text-gray-400'
                      }`}>
                        Tier {investor.tier}
                      </span>
                    </div>
                    <div className="text-sm text-white/70 mb-2">{investor.type}</div>
                    <div className="flex flex-wrap gap-2 mb-2">
                      {investor.focus?.map((f, idx) => (
                        <span key={idx} className="px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-400 text-xs">
                          {f}
                        </span>
                      ))}
                    </div>
                    <div className="text-sm text-white/50 space-y-1">
                      <div>Check Size: {investor.check_size}</div>
                      <div>Stage: {investor.stage}</div>
                      <div className="flex items-center gap-2">
                        <Globe className="w-3 h-3" />
                        {investor.location}
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col gap-2">
                    <a 
                      href={investor.website} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="p-2 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 transition text-cyan-400"
                    >
                      <ArrowUpRight className="w-4 h-4" />
                    </a>
                    <a 
                      href={`mailto:${investor.contact}`}
                      className="p-2 rounded-lg bg-purple-500/20 hover:bg-purple-500/30 transition text-purple-400"
                    >
                      <Mail className="w-4 h-4" />
                    </a>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
        
        {/* Market Position */}
        <div className="glass rounded-xl p-6">
          <h2 className="font-rajdhani text-2xl font-bold mb-4">🎯 Market Position</h2>
          <div className="space-y-4">
            <div>
              <div className="text-sm text-white/60 mb-1">Category</div>
              <div className="font-semibold text-lg">{market.category}</div>
            </div>
            <div>
              <div className="text-sm text-white/60 mb-1">Key Differentiation</div>
              <div className="text-white/90">{market.differentiation}</div>
            </div>
            <div>
              <div className="text-sm text-white/60 mb-1">Market Size</div>
              <div className="text-xl font-bold text-green-400">{market.market_size}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
