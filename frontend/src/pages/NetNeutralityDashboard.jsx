import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Globe, 
  Phone, 
  Mail, 
  TrendingUp, 
  Shield, 
  AlertTriangle,
  Users,
  FileText,
  Code
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function NetNeutralityDashboard() {
  const [activeTab, setActiveTab] = useState('campaigns');
  const [campaigns, setCampaigns] = useState([]);
  const [representatives, setRepresentatives] = useState([]);
  const [internetHealth, setInternetHealth] = useState(null);
  const [zipCode, setZipCode] = useState('');
  const [loading, setLoading] = useState(false);

  // Fetch internet health on mount
  useEffect(() => {
    fetchInternetHealth();
  }, []);

  const fetchInternetHealth = async () => {
    try {
      const response = await fetch(`${API_URL}/api/hybrid/netneutrality/internet-health?region=global`);
      const data = await response.json();
      if (data.success) {
        setInternetHealth(data.health);
      }
    } catch (error) {
      console.error('Failed to fetch internet health:', error);
    }
  };

  const findRepresentatives = async () => {
    if (!zipCode) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/hybrid/netneutrality/representatives/${zipCode}`);
      const data = await response.json();
      if (data.success) {
        setRepresentatives(data.representatives);
      }
    } catch (error) {
      console.error('Failed to find representatives:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCallScript = async (issue) => {
    try {
      const response = await fetch(`${API_URL}/api/hybrid/netneutrality/call-script/${issue}`);
      const data = await response.json();
      if (data.success) {
        // Display script in modal or new section
        console.log('Call Script:', data.script);
        alert(`Call Script:\n\n${data.script.introduction}\n\n${data.script.main_message}\n\nKey Points:\n${data.script.key_points.join('\n')}\n\n${data.script.closing}`);
      }
    } catch (error) {
      console.error('Failed to get call script:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-slate-900 dark:text-white flex items-center gap-3">
              <Globe className="h-10 w-10 text-blue-600" />
              Digital Rights Dashboard
            </h1>
            <p className="text-slate-600 dark:text-slate-400 mt-2">
              Protect net neutrality and internet freedom
            </p>
          </div>
        </div>

        {/* Internet Health Overview */}
        {internetHealth && (
          <Card className="border-2 border-blue-200 dark:border-blue-800">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-green-600" />
                Global Internet Health
              </CardTitle>
              <CardDescription>Real-time monitoring of internet freedom</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">{internetHealth.overall_score}</div>
                  <div className="text-sm text-slate-600 dark:text-slate-400">Overall Score</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">{internetHealth.metrics.content_accessibility}</div>
                  <div className="text-sm text-slate-600 dark:text-slate-400">Accessibility</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-yellow-600">{internetHealth.metrics.privacy_protections}</div>
                  <div className="text-sm text-slate-600 dark:text-slate-400">Privacy</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-orange-600">{internetHealth.metrics.censorship_level}</div>
                  <div className="text-sm text-slate-600 dark:text-slate-400">Censorship</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600">{internetHealth.metrics.net_neutrality_compliance}</div>
                  <div className="text-sm text-slate-600 dark:text-slate-400">Compliance</div>
                </div>
              </div>
              
              {internetHealth.alerts && internetHealth.alerts.length > 0 && (
                <div className="mt-4 space-y-2">
                  <h4 className="font-semibold text-sm flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-orange-600" />
                    Active Alerts
                  </h4>
                  {internetHealth.alerts.map((alert, idx) => (
                    <div key={idx} className="flex items-center gap-2 p-2 bg-orange-50 dark:bg-orange-900/20 rounded">
                      <Badge variant="outline" className="text-orange-700 border-orange-300">
                        {alert.severity}
                      </Badge>
                      <span className="text-sm">{alert.description}</span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Main Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="campaigns" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Campaigns
            </TabsTrigger>
            <TabsTrigger value="contact" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Contact Congress
            </TabsTrigger>
            <TabsTrigger value="monitor" className="flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Monitoring
            </TabsTrigger>
            <TabsTrigger value="widget" className="flex items-center gap-2">
              <Code className="h-4 w-4" />
              Widgets
            </TabsTrigger>
          </TabsList>

          {/* Campaigns Tab */}
          <TabsContent value="campaigns" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Active Campaigns</CardTitle>
                <CardDescription>Join or create campaigns to protect digital rights</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4">
                  <Card className="border border-slate-200 dark:border-slate-700">
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold mb-2">Save Net Neutrality</h3>
                          <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
                            Support strong FCC rules protecting open internet access for all Americans
                          </p>
                          <div className="flex items-center gap-4">
                            <Badge variant="outline" className="text-green-700 border-green-300">
                              12,847 signatures
                            </Badge>
                            <span className="text-sm text-slate-600">Goal: 50,000</span>
                          </div>
                        </div>
                        <Button>Sign Petition</Button>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="border border-slate-200 dark:border-slate-700">
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="text-lg font-semibold mb-2">Stop ISP Throttling</h3>
                          <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
                            Demand transparency and accountability from internet service providers
                          </p>
                          <div className="flex items-center gap-4">
                            <Badge variant="outline" className="text-blue-700 border-blue-300">
                              8,234 signatures
                            </Badge>
                            <span className="text-sm text-slate-600">Goal: 25,000</span>
                          </div>
                        </div>
                        <Button>Sign Petition</Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Contact Congress Tab */}
          <TabsContent value="contact" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Find Your Representatives
                </CardTitle>
                <CardDescription>Contact your representatives about net neutrality</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-2">
                  <Input 
                    placeholder="Enter your ZIP code" 
                    value={zipCode}
                    onChange={(e) => setZipCode(e.target.value)}
                    maxLength={5}
                  />
                  <Button onClick={findRepresentatives} disabled={loading}>
                    {loading ? 'Searching...' : 'Find'}
                  </Button>
                </div>

                {representatives.length > 0 && (
                  <div className="space-y-3">
                    {representatives.map((rep, idx) => (
                      <Card key={idx} className="border border-slate-200 dark:border-slate-700">
                        <CardContent className="pt-6">
                          <div className="flex items-start justify-between">
                            <div>
                              <h3 className="font-semibold">{rep.name}</h3>
                              <p className="text-sm text-slate-600 dark:text-slate-400">{rep.position}</p>
                              <div className="mt-2 space-y-1 text-sm">
                                <div className="flex items-center gap-2">
                                  <Phone className="h-4 w-4" />
                                  {rep.phone}
                                </div>
                                {rep.email && (
                                  <div className="flex items-center gap-2">
                                    <Mail className="h-4 w-4" />
                                    {rep.email}
                                  </div>
                                )}
                              </div>
                            </div>
                            <div className="flex flex-col gap-2">
                              <Button size="sm" onClick={() => getCallScript('net_neutrality')}>
                                Get Call Script
                              </Button>
                              <Button size="sm" variant="outline">
                                Send Email
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Monitoring Tab */}
          <TabsContent value="monitor" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Internet Freedom Monitoring
                </CardTitle>
                <CardDescription>Track censorship and net neutrality violations</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                    <div className="flex items-center gap-2 mb-2">
                      <Shield className="h-5 w-5 text-green-600" />
                      <h3 className="font-semibold text-green-900 dark:text-green-100">No Active Threats Detected</h3>
                    </div>
                    <p className="text-sm text-green-700 dark:text-green-300">
                      Your internet connection is currently unrestricted
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <Card className="border border-slate-200 dark:border-slate-700">
                      <CardContent className="pt-6 text-center">
                        <div className="text-3xl font-bold text-blue-600 mb-2">0</div>
                        <div className="text-sm text-slate-600 dark:text-slate-400">Blocked Sites</div>
                      </CardContent>
                    </Card>
                    <Card className="border border-slate-200 dark:border-slate-700">
                      <CardContent className="pt-6 text-center">
                        <div className="text-3xl font-bold text-green-600 mb-2">Fast</div>
                        <div className="text-sm text-slate-600 dark:text-slate-400">Connection Speed</div>
                      </CardContent>
                    </Card>
                  </div>

                  <Button className="w-full" variant="outline">
                    Run Throttling Test
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Widget Tab */}
          <TabsContent value="widget" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Code className="h-5 w-5" />
                  Embeddable Widgets
                </CardTitle>
                <CardDescription>Add campaign widgets to your website</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 bg-slate-100 dark:bg-slate-800 rounded font-mono text-sm overflow-x-auto">
                    {`<script src="https://nexus.ai/widgets/digitalrights.js"></script>
<script>
  new NexusDigitalRightsWidget({
    campaignId: 'save-net-neutrality',
    type: 'modal',
    theme: 'dark'
  });
</script>`}
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <Button variant="outline">Modal</Button>
                    <Button variant="outline">Banner</Button>
                    <Button variant="outline">Corner</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
