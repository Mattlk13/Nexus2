import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import {
  Bot,
  Plus,
  Play,
  Upload,
  Trash2,
  Terminal,
  CheckCircle,
  AlertCircle,
  Loader2,
  Rocket,
  Code,
  Zap
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';

const AgentStudio = () => {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [testPrompt, setTestPrompt] = useState('');
  const [testResult, setTestResult] = useState(null);
  const [adkStatus, setAdkStatus] = useState(null);

  // Create Agent Form State
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newAgent, setNewAgent] = useState({
    agent_name: '',
    deployment_name: 'development',
    description: '',
    model: 'openai-gpt-oss-120b'
  });

  useEffect(() => {
    loadAdkStatus();
    loadAgents();
  }, []);

  const loadAdkStatus = async () => {
    try {
      const response = await fetch(`${API_URL}/api/adk/status`);
      const data = await response.json();
      setAdkStatus(data);
    } catch (error) {
      console.error('Error loading ADK status:', error);
    }
  };

  const loadAgents = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/adk/agents`);
      const data = await response.json();
      setAgents(data.agents || []);
    } catch (error) {
      console.error('Error loading agents:', error);
    } finally {
      setLoading(false);
    }
  };

  const createAgent = async () => {
    if (!newAgent.agent_name) {
      alert('Please enter an agent name');
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/adk/agents/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newAgent)
      });

      const data = await response.json();
      
      if (response.ok) {
        alert('Agent created successfully!');
        setShowCreateForm(false);
        setNewAgent({
          agent_name: '',
          deployment_name: 'development',
          description: '',
          model: 'openai-gpt-oss-120b'
        });
        loadAgents();
      } else {
        alert(`Error: ${data.detail || 'Failed to create agent'}`);
      }
    } catch (error) {
      alert('Error creating agent');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const testAgent = async () => {
    if (!selectedAgent || !testPrompt) return;

    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/adk/agents/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_name: selectedAgent.agent_name,
          prompt: testPrompt
        })
      });

      const data = await response.json();
      setTestResult(data);
    } catch (error) {
      console.error('Error testing agent:', error);
      setTestResult({ success: false, error: error.message });
    } finally {
      setLoading(false);
    }
  };

  const deployAgent = async (agent) => {
    if (!confirm(`Deploy agent "${agent.agent_name}" to DigitalOcean?`)) return;

    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/adk/agents/deploy`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_name: agent.agent_name,
          deployment_name: agent.deployment_name
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        alert(`Agent deployed successfully!\nURL: ${data.deployment_url}`);
        loadAgents();
      } else {
        alert(`Deployment failed: ${data.detail}`);
      }
    } catch (error) {
      alert('Error deploying agent');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const deleteAgent = async (agentName) => {
    if (!confirm(`Delete agent "${agentName}"? This cannot be undone.`)) return;

    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/adk/agents/${agentName}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        alert('Agent deleted successfully');
        setSelectedAgent(null);
        loadAgents();
      } else {
        alert('Failed to delete agent');
      }
    } catch (error) {
      alert('Error deleting agent');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      created: { color: 'bg-blue-100 text-blue-800', icon: Code, text: 'Created' },
      deployed: { color: 'bg-green-100 text-green-800', icon: CheckCircle, text: 'Deployed' },
      failed: { color: 'bg-red-100 text-red-800', icon: AlertCircle, text: 'Failed' }
    };

    const badge = badges[status] || badges.created;
    const Icon = badge.icon;

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${badge.color}`}>
        <Icon className="w-3 h-3" />
        {badge.text}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
                <Bot className="inline-block w-10 h-10 mr-3 text-purple-600" />
                Agent Studio
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Build, test, and deploy AI agents with DigitalOcean ADK
              </p>
            </div>
            <Button
              onClick={() => setShowCreateForm(true)}
              className="bg-purple-600 hover:bg-purple-700 text-white"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Agent
            </Button>
          </div>
        </div>

        {/* ADK Status */}
        {adkStatus && (
          <Card className="mb-6 border-l-4 border-purple-500">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Zap className="w-5 h-5 text-purple-600" />
                  <div>
                    <span className="font-semibold">DigitalOcean ADK Status: </span>
                    <span className={adkStatus.adk_available ? 'text-green-600' : 'text-red-600'}>
                      {adkStatus.adk_available ? 'Operational' : 'Not Available'}
                    </span>
                  </div>
                </div>
                <div className="flex gap-4 text-sm text-gray-600">
                  <span>Gradient Key: {adkStatus.gradient_key_configured ? '✓' : '✗'}</span>
                  <span>DO Token: {adkStatus.do_token_configured ? '✓' : '✗'}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Create Agent Form */}
        {showCreateForm && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Create New Agent</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Agent Name</label>
                  <Input
                    placeholder="my-ai-agent"
                    value={newAgent.agent_name}
                    onChange={(e) => setNewAgent({ ...newAgent, agent_name: e.target.value })}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Description</label>
                  <Input
                    placeholder="What does this agent do?"
                    value={newAgent.description}
                    onChange={(e) => setNewAgent({ ...newAgent, description: e.target.value })}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Model</label>
                  <select
                    className="w-full p-2 border rounded-lg"
                    value={newAgent.model}
                    onChange={(e) => setNewAgent({ ...newAgent, model: e.target.value })}
                  >
                    <option value="openai-gpt-oss-120b">GPT OSS 120B</option>
                    <option value="meta-llama-3.1-405b-instruct">Llama 3.1 405B</option>
                    <option value="anthropic-claude-3.5-sonnet">Claude 3.5 Sonnet</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Deployment Name</label>
                  <Input
                    placeholder="development"
                    value={newAgent.deployment_name}
                    onChange={(e) => setNewAgent({ ...newAgent, deployment_name: e.target.value })}
                  />
                </div>

                <div className="flex gap-2">
                  <Button
                    onClick={createAgent}
                    disabled={loading}
                    className="bg-purple-600 hover:bg-purple-700"
                  >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Create Agent'}
                  </Button>
                  <Button
                    onClick={() => setShowCreateForm(false)}
                    variant="outline"
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Agents List */}
          <Card>
            <CardHeader>
              <CardTitle>Your Agents ({agents.length})</CardTitle>
            </CardHeader>
            <CardContent>
              {loading && agents.length === 0 ? (
                <div className="text-center py-8">
                  <Loader2 className="w-8 h-8 animate-spin mx-auto text-purple-600" />
                </div>
              ) : agents.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Bot className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No agents yet. Create your first agent to get started!</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {agents.map((agent) => (
                    <div
                      key={agent.agent_name}
                      className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
                        selectedAgent?.agent_name === agent.agent_name
                          ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                          : 'border-gray-200 dark:border-gray-700'
                      }`}
                      onClick={() => setSelectedAgent(agent)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold">{agent.agent_name}</h3>
                            {getStatusBadge(agent.status)}
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                            {agent.description || 'No description'}
                          </p>
                          <div className="flex items-center gap-4 text-xs text-gray-500">
                            <span>Model: {agent.model}</span>
                            <span>Env: {agent.deployment_name}</span>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          {agent.status === 'created' && (
                            <Button
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                deployAgent(agent);
                              }}
                              className="bg-green-600 hover:bg-green-700"
                            >
                              <Rocket className="w-3 h-3" />
                            </Button>
                          )}
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteAgent(agent.agent_name);
                            }}
                          >
                            <Trash2 className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                      {agent.deployment_url && (
                        <div className="mt-2 text-xs text-purple-600 break-all">
                          🔗 {agent.deployment_url}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Agent Testing */}
          <Card>
            <CardHeader>
              <CardTitle>Test Agent</CardTitle>
            </CardHeader>
            <CardContent>
              {selectedAgent ? (
                <div className="space-y-4">
                  <div className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <div className="text-sm font-semibold mb-1">
                      {selectedAgent.agent_name}
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">
                      {selectedAgent.description}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Test Prompt</label>
                    <Input
                      placeholder="Enter a test prompt..."
                      value={testPrompt}
                      onChange={(e) => setTestPrompt(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && testAgent()}
                    />
                  </div>

                  <Button
                    onClick={testAgent}
                    disabled={loading || !testPrompt}
                    className="w-full bg-purple-600 hover:bg-purple-700"
                  >
                    {loading ? (
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    ) : (
                      <Play className="w-4 h-4 mr-2" />
                    )}
                    Test Agent
                  </Button>

                  {testResult && (
                    <div className={`p-4 rounded-lg ${
                      testResult.success
                        ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
                        : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
                    }`}>
                      <div className="flex items-start gap-2">
                        {testResult.success ? (
                          <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                        ) : (
                          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                        )}
                        <div className="flex-1">
                          <div className="font-semibold text-sm mb-1">
                            {testResult.success ? 'Test Successful' : 'Test Failed'}
                          </div>
                          <pre className="text-xs whitespace-pre-wrap break-all">
                            {JSON.stringify(testResult.result || testResult.error, null, 2)}
                          </pre>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <Terminal className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>Select an agent to test</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AgentStudio;
