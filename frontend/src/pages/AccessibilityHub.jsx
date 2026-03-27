import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import axios from 'axios';
import { Eye, Shield, CheckCircle, AlertCircle, Loader2, Palette } from 'lucide-react';
import { API } from '../App';

const AccessibilityHub = () => {
  const [pageUrl, setPageUrl] = useState('');
  const [fgColor, setFgColor] = useState('#000000');
  const [bgColor, setBgColor] = useState('#FFFFFF');
  const [activeTab, setActiveTab] = useState('audit');

  // Fetch capabilities
  const { data: capabilities } = useQuery({
    queryKey: ['accessibility-capabilities'],
    queryFn: async () => {
      const res = await axios.get(`${API}/hybrid/accessibility/capabilities`);
      return res.data;
    }
  });

  // Audit page mutation
  const auditPage = useMutation({
    mutationFn: async (url) => {
      const token = localStorage.getItem('nexus_token');
      const res = await axios.post(
        `${API}/hybrid/accessibility/audit?url=${encodeURIComponent(url)}`,
        {},
        { headers: { Authorization: `Bearer ${token}` }}
      );
      return res.data;
    }
  });

  // Contrast check mutation
  const checkContrast = useMutation({
    mutationFn: async ({ fg, bg }) => {
      const res = await axios.post(
        `${API}/hybrid/accessibility/contrast-check?foreground=${encodeURIComponent(fg)}&background=${encodeURIComponent(bg)}`
      );
      return res.data;
    }
  });

  return (
    <div className="min-h-screen bg-[#050505] text-white pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-green-500 bg-clip-text text-transparent mb-2">
            ♿ Web Accessibility Hub
          </h1>
          <p className="text-gray-400">WCAG compliance, auditing & contrast checking</p>
          {capabilities && (
            <div className="flex gap-4 mt-3">
              {capabilities.tools?.map((tool, idx) => (
                <span key={idx} className="text-xs bg-blue-900/30 border border-blue-700 px-3 py-1 rounded-full">
                  {tool}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6 border-b border-gray-800">
          {['audit', 'contrast'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 capitalize transition-colors ${
                activeTab === tab
                  ? 'text-blue-400 border-b-2 border-blue-400'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Audit Tab */}
        {activeTab === 'audit' && (
          <div className="bg-gray-900/50 backdrop-blur border border-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-6">
              <Eye className="w-6 h-6 text-blue-400" />
              <h2 className="text-2xl font-semibold">Page Accessibility Audit</h2>
            </div>
            
            <div className="space-y-4">
              <input
                type="url"
                placeholder="Enter page URL to audit"
                value={pageUrl}
                onChange={(e) => setPageUrl(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white"
              />
              
              <button
                onClick={() => auditPage.mutate(pageUrl)}
                disabled={!pageUrl || auditPage.isPending}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 px-6 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2"
              >
                {auditPage.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Shield className="w-4 h-4" />
                )}
                Run Audit
              </button>

              {auditPage.isSuccess && auditPage.data && (
                <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <p className="text-2xl font-bold text-blue-400">{auditPage.data.score}/100</p>
                      <p className="text-gray-400 text-sm">Accessibility Score</p>
                    </div>
                    <CheckCircle className="w-12 h-12 text-green-400" />
                  </div>
                  
                  <div className="space-y-2">
                    <p className="text-sm text-gray-400">Issues Found: {auditPage.data.issues?.length || 0}</p>
                    {auditPage.data.recommendations?.map((rec, idx) => (
                      <div key={idx} className="flex items-start gap-2">
                        <AlertCircle className="w-4 h-4 text-yellow-400 mt-0.5" />
                        <p className="text-sm text-gray-300">{rec}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Contrast Tab */}
        {activeTab === 'contrast' && (
          <div className="bg-gray-900/50 backdrop-blur border border-gray-800 rounded-lg p-8">
            <div className="flex items-center gap-3 mb-6">
              <Palette className="w-6 h-6 text-green-400" />
              <h2 className="text-2xl font-semibold">Color Contrast Checker</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Foreground Color</label>
                <input
                  type="color"
                  value={fgColor}
                  onChange={(e) => setFgColor(e.target.value)}
                  className="w-full h-12 rounded-lg cursor-pointer"
                />
                <p className="text-xs text-gray-500 mt-1">{fgColor}</p>
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-2">Background Color</label>
                <input
                  type="color"
                  value={bgColor}
                  onChange={(e) => setBgColor(e.target.value)}
                  className="w-full h-12 rounded-lg cursor-pointer"
                />
                <p className="text-xs text-gray-500 mt-1">{bgColor}</p>
              </div>
            </div>

            {/* Preview */}
            <div className="mb-6 p-8 rounded-lg" style={{ backgroundColor: bgColor }}>
              <p className="text-2xl font-bold" style={{ color: fgColor }}>Sample Text</p>
            </div>

            <button
              onClick={() => checkContrast.mutate({ fg: fgColor, bg: bgColor })}
              disabled={checkContrast.isPending}
              className="bg-green-600 hover:bg-green-700 disabled:bg-gray-700 px-6 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2"
            >
              {checkContrast.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <CheckCircle className="w-4 h-4" />
              )}
              Check Contrast
            </button>

            {checkContrast.isSuccess && checkContrast.data && (
              <div className="mt-6 bg-green-900/30 border border-green-700 rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-3">Contrast Results</h3>
                <div className="space-y-2">
                  <p className="text-gray-300">Ratio: <span className="text-green-400 font-bold">{checkContrast.data.ratio}</span></p>
                  <p className="text-gray-300">
                    WCAG AA: {checkContrast.data.wcag_aa ? (
                      <span className="text-green-400">✅ Pass</span>
                    ) : (
                      <span className="text-red-400">❌ Fail</span>
                    )}
                  </p>
                  <p className="text-gray-300">
                    WCAG AAA: {checkContrast.data.wcag_aaa ? (
                      <span className="text-green-400">✅ Pass</span>
                    ) : (
                      <span className="text-yellow-400">⚠️ Fail</span>
                    )}
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AccessibilityHub;
