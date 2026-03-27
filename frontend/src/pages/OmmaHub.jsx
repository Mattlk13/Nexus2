import React, { useState } from 'react';
import { useQuery, useMutation } from '@tantml:query';
import axios from 'axios';
import { 
  Sparkles, Code, Box, Image, Video, Zap, Users, 
  Play, Loader2, CheckCircle, ArrowRight, Wand2
} from 'lucide-react';
import { BACKEND_URL } from '../App';

// Use v2 API for Omma (self-registered routes)
const OMMA_API = `${BACKEND_URL}/api/v2/hybrid/omma`;

const OmmaHub = () => {
  const [projectType, setProjectType] = useState('app');
  const [description, setDescription] = useState('');
  const [activeTab, setActiveTab] = useState('create');

  // Fetch capabilities
  const { data: capabilities, isLoading } = useQuery({
    queryKey: ['omma-capabilities'],
    queryFn: async () => {
      const res = await axios.get(`${OMMA_API}/capabilities`);
      return res.data;
    }
  });

  // Fetch agents
  const { data: agentsData } = useQuery({
    queryKey: ['omma-agents'],
    queryFn: async () => {
      const res = await axios.get(`${OMMA_API}/agents`);
      return res.data;
    }
  });

  // Create project mutation
  const createProject = useMutation({
    mutationFn: async ({ type, desc }) => {
      const token = localStorage.getItem('nexus_token');
      const res = await axios.post(
        `${OMMA_API}/project?project_type=${type}&description=${encodeURIComponent(desc)}`,
        {},
        { headers: { Authorization: `Bearer ${token}` }}
      );
      return res.data;
    }
  });

  const projectTypes = [
    { id: 'app', name: 'Mobile App', icon: Code, description: 'Create interactive applications', color: 'from-blue-500 to-cyan-500' },
    { id: 'website', name: 'Website', icon: Code, description: 'Build responsive websites', color: 'from-purple-500 to-pink-500' },
    { id: '3d', name: '3D Assets', icon: Box, description: 'Generate 3D models', color: 'from-green-500 to-emerald-500' },
    { id: 'fullstack', name: 'Full Stack', icon: Sparkles, description: 'Complete application with everything', color: 'from-orange-500 to-red-500' }
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Hero Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20 rounded-full mb-4">
            <Sparkles className="w-5 h-5 text-purple-400 animate-pulse" />
            <span className="text-sm font-semibold text-purple-400">
              Multi-Agent AI Platform
            </span>
          </div>
          
          <h1 className="text-5xl font-bold mb-4">
            <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-cyan-400 bg-clip-text text-transparent">
              Omma
            </span>
          </h1>
          
          <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-6">
            Create 3D, apps, and websites with parallel agents
          </p>

          {capabilities && (
            <div className="flex gap-4 justify-center flex-wrap text-sm">
              <div className="flex items-center gap-2 text-gray-400">
                <Code className="w-4 h-4 text-blue-400" />
                <span>Code Generation</span>
              </div>
              <div className="flex items-center gap-2 text-gray-400">
                <Box className="w-4 h-4 text-green-400" />
                <span>3D Generation</span>
              </div>
              <div className="flex items-center gap-2 text-gray-400">
                <Image className="w-4 h-4 text-pink-400" />
                <span>Media Generation</span>
              </div>
              <div className="flex items-center gap-2 text-gray-400">
                <Users className="w-4 h-4 text-purple-400" />
                <span>Parallel Agents</span>
              </div>
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-8 border-b border-gray-800">
          {['create', 'agents', 'features'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 capitalize transition-colors font-semibold ${
                activeTab === tab
                  ? 'text-purple-400 border-b-2 border-purple-400'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Create Project Tab */}
        {activeTab === 'create' && (
          <div className="space-y-8">
            {/* Project Type Selection */}
            <div>
              <h2 className="text-2xl font-semibold mb-4">Choose Project Type</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {projectTypes.map((type) => {
                  const IconComponent = type.icon;
                  return (
                    <button
                      key={type.id}
                      onClick={() => setProjectType(type.id)}
                      className={`p-6 rounded-lg border-2 transition-all ${
                        projectType === type.id
                          ? 'border-purple-400 bg-purple-900/20'
                          : 'border-gray-800 hover:border-gray-700 bg-gray-900/50'
                      }`}
                    >
                      <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${type.color} flex items-center justify-center mb-4`}>
                        <IconComponent className="w-6 h-6 text-white" />
                      </div>
                      <h3 className="text-lg font-semibold mb-2">{type.name}</h3>
                      <p className="text-sm text-gray-400">{type.description}</p>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Description Input */}
            <div className="bg-gray-900/50 backdrop-blur border border-gray-800 rounded-lg p-8">
              <h2 className="text-2xl font-semibold mb-4">Describe Your Project</h2>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="e.g., Create a weather app with 3D globe visualization and real-time data"
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 h-32 resize-none"
              />
              
              <button
                onClick={() => createProject.mutate({ type: projectType, desc: description })}
                disabled={!description || createProject.isPending}
                className="mt-4 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:from-gray-700 disabled:to-gray-700 px-8 py-4 rounded-lg font-semibold transition-all flex items-center gap-2"
              >
                {createProject.isPending ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Initializing Agents...
                  </>
                ) : (
                  <>
                    <Play className="w-5 h-5" />
                    Create with Omma
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>

              {createProject.isSuccess && (
                <div className="mt-6 bg-green-900/30 border border-green-700 rounded-lg p-6">
                  <div className="flex items-center gap-3 mb-3">
                    <CheckCircle className="w-6 h-6 text-green-400" />
                    <h3 className="text-xl font-semibold text-green-400">Project Created!</h3>
                  </div>
                  <div className="space-y-2 text-sm">
                    <p className="text-gray-300">Project ID: <span className="text-purple-400 font-mono">{createProject.data.project_id}</span></p>
                    <p className="text-gray-300">Agents Assigned: {createProject.data.agents_assigned.join(', ')}</p>
                    <p className="text-gray-300">Status: <span className="text-yellow-400">{createProject.data.status}</span></p>
                    <p className="text-gray-300">Estimated Time: {createProject.data.estimated_time}</p>
                  </div>
                  <a
                    href={createProject.data.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-4 inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 font-semibold"
                  >
                    View Project <ArrowRight className="w-4 h-4" />
                  </a>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Agents Tab */}
        {activeTab === 'agents' && agentsData && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {agentsData.agents.map((agent, idx) => (
              <div key={idx} className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-lg p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Users className="w-8 h-8 text-purple-400" />
                  <h3 className="text-xl font-semibold">{agent.name}</h3>
                </div>
                <p className="text-gray-400">{agent.description}</p>
              </div>
            ))}
          </div>
        )}

        {/* Features Tab */}
        {activeTab === 'features' && capabilities && (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-purple-900/20 to-pink-900/20 border border-purple-700/50 rounded-lg p-8">
              <h2 className="text-2xl font-semibold mb-6">Platform Capabilities</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-semibold text-purple-400 mb-3">Code Generation</h3>
                  <ul className="space-y-2">
                    {capabilities.capabilities.code_generation.map((tech, idx) => (
                      <li key={idx} className="flex items-center gap-2 text-gray-300">
                        <Code className="w-4 h-4 text-blue-400" />
                        {tech}
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-green-400 mb-3">3D Generation</h3>
                  <ul className="space-y-2">
                    {capabilities.capabilities['3d_generation'].map((format, idx) => (
                      <li key={idx} className="flex items-center gap-2 text-gray-300">
                        <Box className="w-4 h-4 text-green-400" />
                        {format}
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-pink-400 mb-3">Media Generation</h3>
                  <ul className="space-y-2">
                    {capabilities.capabilities.media_generation.map((media, idx) => (
                      <li key={idx} className="flex items-center gap-2 text-gray-300">
                        <Image className="w-4 h-4 text-pink-400" />
                        {media}
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h3 className="text-lg font-semibold text-cyan-400 mb-3">Parallel Processing</h3>
                  <div className="space-y-2 text-gray-300">
                    <p className="flex items-center gap-2">
                      <Zap className="w-4 h-4 text-yellow-400" />
                      Up to {capabilities.capabilities.max_concurrent_agents} agents
                    </p>
                    <p className="flex items-center gap-2">
                      <CheckCircle className="w-4 h-4 text-green-400" />
                      Real-time orchestration
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex gap-4">
              <a
                href={capabilities.website}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 bg-gray-900 hover:bg-gray-800 border border-gray-700 rounded-lg p-6 text-center transition-colors"
              >
                <Wand2 className="w-8 h-8 text-purple-400 mx-auto mb-2" />
                <p className="font-semibold">Visit Omma</p>
              </a>
              <a
                href={capabilities.product_hunt}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 bg-gray-900 hover:bg-gray-800 border border-gray-700 rounded-lg p-6 text-center transition-colors"
              >
                <Sparkles className="w-8 h-8 text-orange-400 mx-auto mb-2" />
                <p className="font-semibold">Product Hunt</p>
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OmmaHub;
