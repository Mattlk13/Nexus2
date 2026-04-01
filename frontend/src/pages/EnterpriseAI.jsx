import React, { useState, useEffect } from 'react';
import { Sparkles, Search, Users, Video, Plug, Clock, TrendingUp, CheckCircle, AlertCircle } from 'lucide-react';

const API = process.env.REACT_APP_BACKEND_URL;

function EnterpriseAI() {
  const [activeTab, setActiveTab] = useState('research');
  const [capabilities, setCapabilities] = useState(null);
  const [loading, setLoading] = useState(false);

  // Deep Research State
  const [researchQuery, setResearchQuery] = useState('');
  const [researchDepth, setResearchDepth] = useState('standard');
  const [researchResults, setResearchResults] = useState(null);

  // CRM State
  const [contacts, setContacts] = useState([]);
  const [newContact, setNewContact] = useState({
    name: '', email: '', company: '', phone: '', tags: '', notes: ''
  });

  // Meeting Intelligence State
  const [meetingTranscript, setMeetingTranscript] = useState('');
  const [meetingParticipants, setMeetingParticipants] = useState('');
  const [meetingAnalysis, setMeetingAnalysis] = useState(null);

  // MCP State
  const [mcpServers, setMcpServers] = useState([]);

  useEffect(() => {
    fetchCapabilities();
  }, []);

  const fetchCapabilities = async () => {
    try {
      const res = await fetch(`${API}/api/v2/hybrid/enterprise_slack/capabilities`);
      const data = await res.json();
      setCapabilities(data);
    } catch (err) {
      console.error('Failed to fetch capabilities:', err);
    }
  };

  const performResearch = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/v2/hybrid/enterprise_slack/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: researchQuery,
          depth: researchDepth
        })
      });
      const data = await res.json();
      setResearchResults(data);
    } catch (err) {
      console.error('Research failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const createContact = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const contactData = {
        ...newContact,
        tags: newContact.tags.split(',').map(t => t.trim()).filter(Boolean)
      };
      
      const res = await fetch(`${API}/api/v2/hybrid/enterprise_slack/crm/contacts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(contactData)
      });
      
      if (res.ok) {
        fetchContacts();
        setNewContact({ name: '', email: '', company: '', phone: '', tags: '', notes: '' });
      }
    } catch (err) {
      console.error('Failed to create contact:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchContacts = async () => {
    try {
      const res = await fetch(`${API}/api/v2/hybrid/enterprise_slack/crm/contacts`);
      const data = await res.json();
      setContacts(data.contacts || []);
    } catch (err) {
      console.error('Failed to fetch contacts:', err);
    }
  };

  const analyzeMeeting = async () => {
    setLoading(true);
    try {
      const participants = meetingParticipants.split(',').map(p => p.trim()).filter(Boolean);
      
      const res = await fetch(`${API}/api/v2/hybrid/enterprise_slack/meetings/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transcript: meetingTranscript,
          participants
        })
      });
      const data = await res.json();
      setMeetingAnalysis(data.analysis);
    } catch (err) {
      console.error('Meeting analysis failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchMCPServers = async () => {
    try {
      const res = await fetch(`${API}/api/v2/hybrid/enterprise_slack/mcp/servers`);
      const data = await res.json();
      setMcpServers(Object.entries(data.servers || {}));
    } catch (err) {
      console.error('Failed to fetch MCP servers:', err);
    }
  };

  useEffect(() => {
    if (activeTab === 'crm') fetchContacts();
    if (activeTab === 'mcp') fetchMCPServers();
  }, [activeTab]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <Sparkles className="w-8 h-8 text-purple-600" />
                <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  Enterprise AI Suite
                </h1>
              </div>
              <p className="text-gray-600">30+ Slack-inspired AI features for enterprise productivity</p>
            </div>
            {capabilities && (
              <div className="text-right">
                <div className="text-3xl font-bold text-purple-600">{capabilities.total_features}+</div>
                <div className="text-sm text-gray-600">AI Features</div>
              </div>
            )}
          </div>

          {/* Capabilities Grid */}
          {capabilities && (
            <div className="grid grid-cols-4 gap-4 mt-6">
              {capabilities.categories.map((cat, idx) => (
                <div key={idx} className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-4">
                  <div className="font-semibold text-purple-900 mb-1">{cat.name}</div>
                  <div className="text-xs text-gray-600">{cat.features.length} features</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-t-2xl shadow-lg">
          <div className="flex border-b">
            {[
              { id: 'research', label: 'Deep Research', icon: Search },
              { id: 'crm', label: 'Native CRM', icon: Users },
              { id: 'meetings', label: 'Meeting Intel', icon: Video },
              { id: 'mcp', label: 'MCP Integration', icon: Plug }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-6 py-4 font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'text-purple-600 border-b-2 border-purple-600'
                    : 'text-gray-600 hover:text-purple-600'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-b-2xl shadow-lg p-8">
          {/* Deep Research Tab */}
          {activeTab === 'research' && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">🔍 Deep Research Mode</h2>
              
              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Research Query</label>
                  <input
                    type="text"
                    value={researchQuery}
                    onChange={(e) => setResearchQuery(e.target.value)}
                    placeholder="Enter your research topic..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Research Depth</label>
                  <select
                    value={researchDepth}
                    onChange={(e) => setResearchDepth(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="standard">Standard (2 phases)</option>
                    <option value="deep">Deep (4 phases)</option>
                    <option value="comprehensive">Comprehensive (7 phases)</option>
                  </select>
                </div>

                <button
                  onClick={performResearch}
                  disabled={loading || !researchQuery}
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50"
                >
                  {loading ? 'Researching...' : 'Start Research'}
                </button>
              </div>

              {researchResults && (
                <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-gray-900">Research Results</h3>
                    <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                      {researchResults.phases_completed} phases completed
                    </span>
                  </div>

                  <div className="space-y-4">
                    {researchResults.findings.map((finding, idx) => (
                      <div key={idx} className="bg-white rounded-lg p-4 shadow-sm">
                        <div className="font-semibold text-purple-900 mb-2">{finding.phase}</div>
                        {finding.content && <p className="text-gray-700">{finding.content}</p>}
                        {finding.insights && (
                          <ul className="list-disc list-inside text-gray-700 space-y-1">
                            {finding.insights.map((insight, i) => <li key={i}>{insight}</li>)}
                          </ul>
                        )}
                        {finding.summary && <pre className="text-sm text-gray-700 whitespace-pre-wrap mt-2">{finding.summary}</pre>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Native CRM Tab */}
          {activeTab === 'crm' && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">👥 Native Lightweight CRM</h2>
              
              <form onSubmit={createContact} className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl p-6 mb-6">
                <h3 className="font-bold text-lg mb-4">Add New Contact</h3>
                <div className="grid grid-cols-2 gap-4">
                  <input
                    type="text"
                    placeholder="Name *"
                    value={newContact.name}
                    onChange={(e) => setNewContact({...newContact, name: e.target.value})}
                    required
                    className="px-4 py-2 border rounded-lg"
                  />
                  <input
                    type="email"
                    placeholder="Email *"
                    value={newContact.email}
                    onChange={(e) => setNewContact({...newContact, email: e.target.value})}
                    required
                    className="px-4 py-2 border rounded-lg"
                  />
                  <input
                    type="text"
                    placeholder="Company"
                    value={newContact.company}
                    onChange={(e) => setNewContact({...newContact, company: e.target.value})}
                    className="px-4 py-2 border rounded-lg"
                  />
                  <input
                    type="tel"
                    placeholder="Phone"
                    value={newContact.phone}
                    onChange={(e) => setNewContact({...newContact, phone: e.target.value})}
                    className="px-4 py-2 border rounded-lg"
                  />
                  <input
                    type="text"
                    placeholder="Tags (comma-separated)"
                    value={newContact.tags}
                    onChange={(e) => setNewContact({...newContact, tags: e.target.value})}
                    className="px-4 py-2 border rounded-lg"
                  />
                  <textarea
                    placeholder="Notes"
                    value={newContact.notes}
                    onChange={(e) => setNewContact({...newContact, notes: e.target.value})}
                    className="px-4 py-2 border rounded-lg col-span-2"
                    rows="2"
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="mt-4 w-full bg-purple-600 text-white py-2 rounded-lg font-semibold hover:bg-purple-700 transition-colors"
                >
                  Add Contact
                </button>
              </form>

              <div className="space-y-3">
                <h3 className="font-bold text-lg">Contacts ({contacts.length})</h3>
                {contacts.map((contact, idx) => (
                  <div key={idx} className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex justify-between items-start">
                      <div>
                        <div className="font-semibold text-lg">{contact.name}</div>
                        <div className="text-gray-600 text-sm">{contact.email}</div>
                        {contact.company && <div className="text-gray-500 text-sm">{contact.company}</div>}
                      </div>
                      {contact.tags && contact.tags.length > 0 && (
                        <div className="flex gap-1 flex-wrap">
                          {contact.tags.map((tag, i) => (
                            <span key={i} className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs">
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {contacts.length === 0 && (
                  <p className="text-gray-500 text-center py-8">No contacts yet. Add your first contact above!</p>
                )}
              </div>
            </div>
          )}

          {/* Meeting Intelligence Tab */}
          {activeTab === 'meetings' && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">🎯 Meeting Intelligence</h2>
              
              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Meeting Transcript</label>
                  <textarea
                    value={meetingTranscript}
                    onChange={(e) => setMeetingTranscript(e.target.value)}
                    placeholder="Paste meeting transcript or notes here..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 h-32"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Participants (comma-separated)</label>
                  <input
                    type="text"
                    value={meetingParticipants}
                    onChange={(e) => setMeetingParticipants(e.target.value)}
                    placeholder="John Doe, Jane Smith, Alex Johnson"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                </div>

                <button
                  onClick={analyzeMeeting}
                  disabled={loading || !meetingTranscript || !meetingParticipants}
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50"
                >
                  {loading ? 'Analyzing...' : 'Analyze Meeting'}
                </button>
              </div>

              {meetingAnalysis && (
                <div className="space-y-4">
                  <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl p-6">
                    <h3 className="font-bold text-lg mb-3">📝 Summary</h3>
                    <p className="text-gray-700">{meetingAnalysis.summary}</p>
                  </div>

                  <div className="bg-white border rounded-xl p-6">
                    <h3 className="font-bold text-lg mb-3">✅ Action Items</h3>
                    <div className="space-y-3">
                      {meetingAnalysis.action_items.map((item, idx) => (
                        <div key={idx} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                          <CheckCircle className="w-5 h-5 text-blue-600 mt-1 flex-shrink-0" />
                          <div className="flex-1">
                            <div className="font-medium">{item.task}</div>
                            <div className="text-sm text-gray-600">
                              Assigned: {item.assigned_to} • Due: {item.due_date}
                            </div>
                          </div>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            item.priority === 'high' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {item.priority}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white border rounded-xl p-6">
                      <h3 className="font-bold text-lg mb-3">🎯 Key Points</h3>
                      <ul className="space-y-2">
                        {meetingAnalysis.key_points.map((point, idx) => (
                          <li key={idx} className="text-gray-700 text-sm">• {point}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="bg-white border rounded-xl p-6">
                      <h3 className="font-bold text-lg mb-3">✨ Decisions Made</h3>
                      <ul className="space-y-2">
                        {meetingAnalysis.decisions_made.map((decision, idx) => (
                          <li key={idx} className="text-gray-700 text-sm">• {decision}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  <div className="bg-green-50 border border-green-200 rounded-xl p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-bold text-green-900">Meeting Sentiment</div>
                        <div className="text-green-700 capitalize">{meetingAnalysis.sentiment}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-green-900">Engagement Score</div>
                        <div className="text-2xl font-bold text-green-600">{meetingAnalysis.engagement_score}/10</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* MCP Integration Tab */}
          {activeTab === 'mcp' && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">🔌 MCP Integration Hub</h2>
              <p className="text-gray-600 mb-6">Model Context Protocol servers for advanced integrations</p>
              
              <div className="grid grid-cols-2 gap-4">
                {mcpServers.map(([name, info], idx) => (
                  <div key={idx} className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-xl p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-start justify-between mb-3">
                      <Plug className="w-8 h-8 text-purple-600" />
                      <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
                        {info.status}
                      </span>
                    </div>
                    <h3 className="font-bold text-lg capitalize mb-2">{name.replace('_', ' ')}</h3>
                    <p className="text-sm text-gray-600">{info.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default EnterpriseAI;
