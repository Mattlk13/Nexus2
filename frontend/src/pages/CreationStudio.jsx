import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Video, Image as ImageIcon, Music, FileText, Code, Sparkles } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CreationStudio = () => {
  const [activeTab, setActiveTab] = useState('video');
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const tools = [
    { id: 'video', name: 'AI Video', icon: Video, service: 'sora_video', color: 'from-purple-500 to-pink-500' },
    { id: 'image', name: 'AI Image', icon: ImageIcon, service: 'gpt_image', color: 'from-blue-500 to-cyan-500' },
    { id: 'audio', name: 'AI Voice', icon: Music, service: 'elevenlabs', color: 'from-green-500 to-emerald-500' },
    { id: 'ebook', name: 'E-Book', icon: FileText, service: 'crewai', color: 'from-orange-500 to-red-500' },
    { id: 'code', name: 'Code Gen', icon: Code, service: 'groq', color: 'from-indigo-500 to-purple-500' },
  ];

  const activeTool = tools.find(t => t.id === activeTab);

  const generate = async () => {
    if (!prompt.trim()) return;
    
    setLoading(true);
    try {
      const endpoint = activeTab === 'video' ? 'generate' : 
                      activeTab === 'image' ? 'generate' :
                      activeTab === 'audio' ? 'synthesize' : 'chat';
      
      const response = await fetch(`${API_URL}/api/v2/hybrid/${activeTool.service}/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          prompt,
          content: prompt,
          message: prompt,
          text: prompt 
        })
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Generation error:', error);
      setResult({ error: 'Generation failed. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            ✨ Creation Studio
          </h1>
          <p className="text-gray-600 mt-2">AI-powered content creation tools</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          
          {/* Sidebar - Tools */}
          <div className="space-y-2">
            {tools.map(tool => {
              const Icon = tool.icon;
              return (
                <Button
                  key={tool.id}
                  variant={activeTab === tool.id ? 'default' : 'ghost'}
                  className="w-full justify-start"
                  onClick={() => setActiveTab(tool.id)}
                >
                  <Icon className="h-5 w-5 mr-3" />
                  {tool.name}
                </Button>
              );
            })}
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <Card className="shadow-xl">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <div className={`h-10 w-10 rounded-lg bg-gradient-to-br ${activeTool.color} flex items-center justify-center text-white mr-3`}>
                    {React.createElement(activeTool.icon, { className: 'h-6 w-6' })}
                  </div>
                  {activeTool.name}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                
                {/* Input Area */}
                <div>
                  <label className="text-sm font-medium mb-2 block">
                    What do you want to create?
                  </label>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder={`Describe your ${activeTool.name.toLowerCase()}...`}
                    className="w-full min-h-[120px] p-4 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>

                {/* Generate Button */}
                <Button
                  onClick={generate}
                  disabled={loading || !prompt.trim()}
                  className="w-full"
                  size="lg"
                >
                  {loading ? (
                    <>
                      <Sparkles className="h-5 w-5 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-5 w-5 mr-2" />
                      Generate {activeTool.name}
                    </>
                  )}
                </Button>

                {/* Result Area */}
                {result && (
                  <div className="mt-6 p-6 bg-gray-50 rounded-lg">
                    <h3 className="font-semibold mb-3">Result:</h3>
                    {result.error ? (
                      <p className="text-red-600">{result.error}</p>
                    ) : (
                      <div className="space-y-2">
                        {result.video_base64 && (
                          <p className="text-green-600">✅ Video generated! (Base64 data received)</p>
                        )}
                        {result.image_base64 && (
                          <p className="text-green-600">✅ Image generated! (Base64 data received)</p>
                        )}
                        {result.response && (
                          <p className="text-gray-800 whitespace-pre-wrap">{result.response}</p>
                        )}
                        {result.note && (
                          <p className="text-sm text-gray-500">{result.note}</p>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {/* Info */}
                <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-800">
                    <strong>Powered by:</strong> {activeTool.service} • 
                    <strong className="ml-2">Status:</strong> Active •
                    <strong className="ml-2">AI Model:</strong> Latest
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreationStudio;
