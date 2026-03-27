import React from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { motion } from "framer-motion";
import { toast } from "sonner";
import {
  Github, GitBranch, Star, GitFork, CheckCircle, Loader2,
  RefreshCw, ExternalLink, AlertCircle
} from "lucide-react";
import { useAuth, API } from "../App";

export const GitHubConnectionPage = () => {
  const { user, token } = useAuth();
  const queryClient = useQueryClient();

  // Get connection status
  const { data: status, isLoading } = useQuery({
    queryKey: ["github-connection-status"],
    queryFn: () => axios.get(`${API}/github/connection-status`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.data),
    enabled: !!token
  });

  // Initiate OAuth
  const connectGitHub = useMutation({
    mutationFn: () => axios.get(`${API}/auth/github/initiate`, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.data),
    onSuccess: (data) => {
      if (data.demo_mode) {
        toast.error("GitHub OAuth not configured on server");
      } else if (data.auth_url) {
        // Redirect to GitHub OAuth
        window.location.href = data.auth_url;
      }
    },
    onError: () => {
      toast.error("Failed to initiate GitHub connection");
    }
  });

  // Sync repositories
  const syncRepos = useMutation({
    mutationFn: () => axios.post(`${API}/github/sync-repos`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    }).then(r => r.data),
    onSuccess: (data) => {
      toast.success(`Synced ${data.repositories_count} repositories`);
      queryClient.invalidateQueries(["github-connection-status"]);
    },
    onError: () => {
      toast.error("Failed to sync repositories");
    }
  });

  if (isLoading) {
    return (
      <div className="min-h-screen pt-28 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
      </div>
    );
  }

  const isConnected = status?.github?.connected;
  const githubUsername = status?.github?.username;
  const reposCount = status?.github?.repos_synced || 0;

  return (
    <div className="min-h-screen pt-28 pb-20 px-4 sm:px-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="font-rajdhani text-4xl font-bold mb-2">
            <span className="gradient-text">GitHub Integration</span>
          </h1>
          <p className="text-white/60">Connect your GitHub account to sync repositories and track your projects</p>
        </div>

        {/* Connection Status Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-xl p-8 mb-6"
        >
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className={`w-16 h-16 rounded-xl flex items-center justify-center ${
                isConnected 
                  ? 'bg-gradient-to-br from-green-500 to-emerald-600' 
                  : 'bg-gradient-to-br from-gray-600 to-gray-700'
              }`}>
                <Github className="w-8 h-8 text-white" />
              </div>
              <div>
                <h2 className="font-rajdhani text-2xl font-bold mb-1">
                  {isConnected ? `Connected as @${githubUsername}` : 'Not Connected'}
                </h2>
                <p className="text-white/60 text-sm">
                  {isConnected 
                    ? 'Your GitHub account is linked to NEXUS' 
                    : 'Connect your GitHub to unlock repository features'}
                </p>
              </div>
            </div>
            
            {isConnected && (
              <div className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-500/20 border border-green-500/30">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="text-green-400 font-semibold text-sm">Active</span>
              </div>
            )}
          </div>

          {isConnected ? (
            <div className="space-y-4">
              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="p-4 rounded-lg bg-white/5">
                  <div className="flex items-center gap-2 mb-2">
                    <GitBranch className="w-4 h-4 text-cyan-400" />
                    <span className="text-sm text-white/60">Repositories</span>
                  </div>
                  <p className="text-2xl font-bold">{reposCount}</p>
                </div>
                <div className="p-4 rounded-lg bg-white/5">
                  <div className="flex items-center gap-2 mb-2">
                    <Star className="w-4 h-4 text-yellow-400" />
                    <span className="text-sm text-white/60">Total Stars</span>
                  </div>
                  <p className="text-2xl font-bold">-</p>
                </div>
                <div className="p-4 rounded-lg bg-white/5">
                  <div className="flex items-center gap-2 mb-2">
                    <GitFork className="w-4 h-4 text-purple-400" />
                    <span className="text-sm text-white/60">Total Forks</span>
                  </div>
                  <p className="text-2xl font-bold">-</p>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <button
                  onClick={() => syncRepos.mutate()}
                  disabled={syncRepos.isPending}
                  className="btn-primary px-6 py-3 rounded-lg flex items-center gap-2"
                >
                  {syncRepos.isPending ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <RefreshCw className="w-4 h-4" />
                  )}
                  Sync Repositories
                </button>
                
                <a
                  href={`https://github.com/${githubUsername}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-6 py-3 rounded-lg bg-white/10 hover:bg-white/20 transition-colors flex items-center gap-2"
                >
                  <ExternalLink className="w-4 h-4" />
                  View on GitHub
                </a>
              </div>
            </div>
          ) : (
            <div className="text-center py-6">
              <button
                onClick={() => connectGitHub.mutate()}
                disabled={connectGitHub.isPending}
                className="btn-primary px-8 py-4 rounded-lg text-lg font-semibold flex items-center gap-3 mx-auto"
              >
                {connectGitHub.isPending ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Github className="w-5 h-5" />
                )}
                Connect GitHub Account
              </button>
              <p className="text-white/40 text-sm mt-4">
                You'll be redirected to GitHub to authorize the connection
              </p>
            </div>
          )}
        </motion.div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass rounded-xl p-6"
        >
          <h3 className="font-rajdhani text-xl font-bold mb-4">What you can do with GitHub integration:</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              {
                icon: GitBranch,
                title: "Repository Sync",
                description: "Automatically sync all your GitHub repositories to NEXUS"
              },
              {
                icon: Star,
                title: "Track Activity",
                description: "Monitor stars, forks, and contributions across your projects"
              },
              {
                icon: GitFork,
                title: "CI/CD Integration",
                description: "Connect your deployment pipelines and monitor build status"
              },
              {
                icon: CheckCircle,
                title: "Showcase Work",
                description: "Display your GitHub projects on your NEXUS profile"
              }
            ].map((feature, idx) => (
              <div key={idx} className="flex gap-3 p-4 rounded-lg bg-white/5">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center flex-shrink-0">
                  <feature.icon className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h4 className="font-semibold mb-1">{feature.title}</h4>
                  <p className="text-sm text-white/60">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Info Alert */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mt-6 p-4 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-start gap-3"
        >
          <AlertCircle className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm text-cyan-100/80">
              <strong>Privacy Notice:</strong> NEXUS only requests access to public repository information. 
              We never access your private code or make changes to your repositories without explicit permission.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};
