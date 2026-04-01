import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Users, DollarSign, TrendingUp, Activity, AlertCircle, CheckCircle } from 'lucide-react';

const AdminDashboard = () => {
  const [stats, setStats] = useState({
    totalUsers: 0,
    activeUsers: 0,
    totalRevenue: 0,
    aiRequests: 0,
    systemHealth: 'healthy'
  });

  const [aiServices, setAiServices] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      // Load stats
      setStats({
        totalUsers: 12458,
        activeUsers: 3421,
        totalRevenue: 45678.90,
        aiRequests: 156789,
        systemHealth: 'healthy'
      });

      // Load AI services status
      const services = [
        { name: 'Sora 2 Video', status: 'active', requests: 1234, uptime: '99.9%' },
        { name: 'GPT Image 1.5', status: 'active', requests: 5678, uptime: '99.8%' },
        { name: 'Groq Cloud', status: 'active', requests: 9012, uptime: '100%' },
        { name: 'CrewAI', status: 'active', requests: 3456, uptime: '99.7%' },
        { name: 'LangGraph', status: 'active', requests: 2345, uptime: '99.9%' },
        { name: 'AutoGen', status: 'active', requests: 1789, uptime: '99.8%' },
        { name: 'OpenClaw', status: 'active', requests: 4567, uptime: '99.9%' },
        { name: 'ElevenLabs', status: 'active', requests: 6789, uptime: '100%' },
      ];
      setAiServices(services);

      // Load recent activity
      setRecentActivity([
        { type: 'user', message: 'New user registration: alice@example.com', time: '2m ago' },
        { type: 'sale', message: 'Marketplace sale: $29.99', time: '5m ago' },
        { type: 'ai', message: 'AI Video generated (Sora 2)', time: '8m ago' },
        { type: 'error', message: 'Rate limit reached for user #1234', time: '15m ago' },
        { type: 'success', message: 'Database backup completed', time: '30m ago' },
      ]);
    } catch (error) {
      console.error('Load dashboard error:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-red-600 to-purple-600 bg-clip-text text-transparent flex items-center">
            🎛️ Admin Dashboard
          </h1>
          <p className="text-gray-600 mt-2">Monitor and manage NEXUS platform</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Users</p>
                  <p className="text-3xl font-bold">{stats.totalUsers.toLocaleString()}</p>
                  <p className="text-xs text-green-600 mt-1">↑ 12% this month</p>
                </div>
                <Users className="h-12 w-12 text-blue-600 opacity-20" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Active Now</p>
                  <p className="text-3xl font-bold">{stats.activeUsers.toLocaleString()}</p>
                  <p className="text-xs text-green-600 mt-1">↑ 5% vs yesterday</p>
                </div>
                <Activity className="h-12 w-12 text-green-600 opacity-20" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Revenue</p>
                  <p className="text-3xl font-bold">${(stats.totalRevenue / 1000).toFixed(1)}K</p>
                  <p className="text-xs text-green-600 mt-1">↑ 23% this month</p>
                </div>
                <DollarSign className="h-12 w-12 text-purple-600 opacity-20" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">AI Requests</p>
                  <p className="text-3xl font-bold">{(stats.aiRequests / 1000).toFixed(0)}K</p>
                  <p className="text-xs text-green-600 mt-1">↑ 45% this week</p>
                </div>
                <TrendingUp className="h-12 w-12 text-orange-600 opacity-20" />
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          
          {/* AI Services Status */}
          <Card>
            <CardHeader>
              <CardTitle>AI Services Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {aiServices.map((service, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <CheckCircle className="h-5 w-5 text-green-600" />
                      <div>
                        <p className="font-medium">{service.name}</p>
                        <p className="text-xs text-gray-600">{service.requests.toLocaleString()} requests today</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">
                        {service.status}
                      </span>
                      <p className="text-xs text-gray-600 mt-1">{service.uptime} uptime</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentActivity.map((activity, idx) => {
                  const icons = {
                    user: <Users className="h-5 w-5 text-blue-600" />,
                    sale: <DollarSign className="h-5 w-5 text-green-600" />,
                    ai: <Activity className="h-5 w-5 text-purple-600" />,
                    error: <AlertCircle className="h-5 w-5 text-red-600" />,
                    success: <CheckCircle className="h-5 w-5 text-green-600" />
                  };

                  return (
                    <div key={idx} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                      {icons[activity.type]}
                      <div className="flex-1">
                        <p className="text-sm">{activity.message}</p>
                        <p className="text-xs text-gray-500 mt-1">{activity.time}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* System Health */}
          <Card>
            <CardHeader>
              <CardTitle>System Health</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm">CPU Usage</span>
                    <span className="text-sm font-medium">42%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-green-600 h-2 rounded-full" style={{ width: '42%' }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm">Memory Usage</span>
                    <span className="text-sm font-medium">68%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-yellow-600 h-2 rounded-full" style={{ width: '68%' }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm">Disk Usage</span>
                    <span className="text-sm font-medium">28%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-green-600 h-2 rounded-full" style={{ width: '28%' }} />
                  </div>
                </div>

                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm">API Response Time</span>
                    <span className="text-sm font-medium">145ms</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-green-600 h-2 rounded-full" style={{ width: '35%' }} />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3">
                <Button variant="outline" className="h-20">
                  <div className="text-center">
                    <Users className="h-6 w-6 mx-auto mb-1" />
                    <p className="text-sm">Manage Users</p>
                  </div>
                </Button>
                <Button variant="outline" className="h-20">
                  <div className="text-center">
                    <Activity className="h-6 w-6 mx-auto mb-1" />
                    <p className="text-sm">View Logs</p>
                  </div>
                </Button>
                <Button variant="outline" className="h-20">
                  <div className="text-center">
                    <TrendingUp className="h-6 w-6 mx-auto mb-1" />
                    <p className="text-sm">Analytics</p>
                  </div>
                </Button>
                <Button variant="outline" className="h-20">
                  <div className="text-center">
                    <DollarSign className="h-6 w-6 mx-auto mb-1" />
                    <p className="text-sm">Revenue</p>
                  </div>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
