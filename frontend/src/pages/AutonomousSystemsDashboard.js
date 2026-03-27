import React, { useState, useEffect } from 'react';
import { Activity, Zap, GitBranch, CheckCircle, XCircle, Clock, Play, Pause, RefreshCw } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AutonomousSystemsDashboard = () => {
  const [systems, setSystems] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchSystemsStatus = async () => {
    try {
      setRefreshing(true);
      const token = localStorage.getItem('token');
      if (!token) {
        // Handle unauthenticated state gracefully
        setSystems({
          testing: { last_test_run: null, auto_fix_enabled: true, coverage_threshold: 80, test_history_count: 0, performance_baselines: 0 },
          cicd: { auto_deploy_enabled: false, rollback_enabled: true, deployment_count: 0, health_check_count: 0, last_health_check: null },
          development: { active_task: null, queued_tasks: 0, completed_tasks: 0, failed_tasks: 0, task_queue: [] },
          philosophy: "Self-testing, self-deploying, self-improving platform"
        });
        setError('Please sign in to access full features');
        setLoading(false);
        setRefreshing(false);
        return;
      }

      const response = await axios.get(`${API_URL}/api/autonomous-systems/status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSystems(response.data);
      setError(null);
    } catch (err) {
      // If unauthorized, show demo data
      if (err.response?.status === 401 || err.response?.status === 403) {
        setSystems({
          testing: { last_test_run: null, auto_fix_enabled: true, coverage_threshold: 80, test_history_count: 0, performance_baselines: 0 },
          cicd: { auto_deploy_enabled: false, rollback_enabled: true, deployment_count: 0, health_check_count: 0, last_health_check: null },
          development: { active_task: null, queued_tasks: 0, completed_tasks: 0, failed_tasks: 0, task_queue: [] },
          philosophy: "Self-testing, self-deploying, self-improving platform"
        });
        setError('Sign in required for full access');
      } else {
        setError(err.response?.data?.detail || 'Failed to fetch system status');
      }
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchSystemsStatus();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchSystemsStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const startAllSystems = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/api/autonomous-systems/start-all`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert('All autonomous systems started!');
      fetchSystemsStatus();
    } catch (err) {
      alert('Failed to start systems: ' + (err.response?.data?.detail || err.message));
    }
  };

  const runAudit = async () => {
    try {
      setRefreshing(true);
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API_URL}/api/autonomous-systems/cicd/audit`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert(`Audit Complete! Score: ${response.data.overall_score.toFixed(1)}/100`);
      fetchSystemsStatus();
    } catch (err) {
      alert('Failed to run audit: ' + (err.response?.data?.detail || err.message));
    } finally {
      setRefreshing(false);
    }
  };

  const runTests = async () => {
    try {
      setRefreshing(true);
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API_URL}/api/autonomous-systems/testing/run`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      alert(`Tests Complete! Status: ${response.data.overall_status}`);
      fetchSystemsStatus();
    } catch (err) {
      alert('Failed to run tests: ' + (err.response?.data?.detail || err.message));
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-cyan-400 animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading autonomous systems...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-red-400">{error}</p>
          <button
            onClick={fetchSystemsStatus}
            className="mt-4 px-6 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
              Autonomous Systems Dashboard
            </h1>
            <p className="text-gray-400 mt-2">{systems?.philosophy}</p>
          </div>
          <button
            onClick={fetchSystemsStatus}
            disabled={refreshing}
            className="p-3 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 text-cyan-400 ${refreshing ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={startAllSystems}
            className="flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 rounded-xl transition-all"
          >
            <Play className="w-5 h-5" />
            Start All Systems
          </button>
          <button
            onClick={runAudit}
            disabled={refreshing}
            className="flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 rounded-xl transition-all disabled:opacity-50"
          >
            <Activity className="w-5 h-5" />
            Run Code Audit
          </button>
          <button
            onClick={runTests}
            disabled={refreshing}
            className="flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 rounded-xl transition-all disabled:opacity-50"
          >
            <CheckCircle className="w-5 h-5" />
            Run All Tests
          </button>
        </div>
      </div>

      {/* System Cards */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Testing System */}
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-purple-500/20 rounded-lg">
              <CheckCircle className="w-6 h-6 text-purple-400" />
            </div>
            <h2 className="text-xl font-semibold">Testing System</h2>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Auto-Fix</span>
              <span className={`px-3 py-1 rounded-full text-sm ${systems?.testing?.auto_fix_enabled ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                {systems?.testing?.auto_fix_enabled ? 'Enabled' : 'Disabled'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Coverage Threshold</span>
              <span className="text-white font-semibold">{systems?.testing?.coverage_threshold}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Test Runs</span>
              <span className="text-white font-semibold">{systems?.testing?.test_history_count}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Last Run</span>
              <span className="text-white font-semibold">
                {systems?.testing?.last_test_run ? 'Recently' : 'Never'}
              </span>
            </div>
          </div>
        </div>

        {/* CI/CD System */}
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-cyan-500/20 rounded-lg">
              <GitBranch className="w-6 h-6 text-cyan-400" />
            </div>
            <h2 className="text-xl font-semibold">CI/CD System</h2>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Auto-Deploy</span>
              <span className={`px-3 py-1 rounded-full text-sm ${systems?.cicd?.auto_deploy_enabled ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                {systems?.cicd?.auto_deploy_enabled ? 'Enabled' : 'Manual'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Rollback</span>
              <span className={`px-3 py-1 rounded-full text-sm ${systems?.cicd?.rollback_enabled ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                {systems?.cicd?.rollback_enabled ? 'Enabled' : 'Disabled'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Deployments</span>
              <span className="text-white font-semibold">{systems?.cicd?.deployment_count}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Health Checks</span>
              <span className="text-white font-semibold">{systems?.cicd?.health_check_count}</span>
            </div>
          </div>
        </div>

        {/* Development System */}
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-pink-500/20 rounded-lg">
              <Zap className="w-6 h-6 text-pink-400" />
            </div>
            <h2 className="text-xl font-semibold">Dev System</h2>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Active Task</span>
              <span className="text-white font-semibold">
                {systems?.development?.active_task ? 'Working' : 'Idle'}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Queued</span>
              <span className="text-white font-semibold">{systems?.development?.queued_tasks}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Completed</span>
              <span className="text-green-400 font-semibold">{systems?.development?.completed_tasks}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-400">Failed</span>
              <span className="text-red-400 font-semibold">{systems?.development?.failed_tasks}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutonomousSystemsDashboard;