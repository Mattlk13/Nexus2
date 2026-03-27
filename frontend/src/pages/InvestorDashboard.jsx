import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, Users, DollarSign, Target } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function InvestorDashboard() {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await fetch(`${API_URL}/api/hybrid/investor-dashboard/metrics`);
      const data = await response.json();
      if (data.success) {
        setMetrics(data.metrics);
      }
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-blue-50 dark:from-slate-900 dark:to-slate-800 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <h1 className="text-4xl font-bold flex items-center gap-3">
          <TrendingUp className="h-10 w-10 text-emerald-600" />
          Investor Dashboard
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <Users className="h-8 w-8 text-blue-600" />
                <div className="text-right">
                  <div className="text-2xl font-bold">2,450</div>
                  <div className="text-sm text-slate-600">Total Investors</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <DollarSign className="h-8 w-8 text-green-600" />
                <div className="text-right">
                  <div className="text-2xl font-bold">$45M</div>
                  <div className="text-sm text-slate-600">Funding Raised</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <Target className="h-8 w-8 text-purple-600" />
                <div className="text-right">
                  <div className="text-2xl font-bold">125</div>
                  <div className="text-sm text-slate-600">Active Leads</div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <TrendingUp className="h-8 w-8 text-orange-600" />
                <div className="text-right">
                  <div className="text-2xl font-bold">23%</div>
                  <div className="text-sm text-slate-600">Conversion Rate</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Investment Pipeline</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {['Discovery', 'Qualification', 'Pitch', 'Due Diligence', 'Closed'].map((stage, idx) => (
                <div key={stage} className="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-800 rounded">
                  <span className="font-medium">{stage}</span>
                  <span className="text-slate-600">{[125, 85, 45, 20, 8][idx]} deals</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
