import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../App";
import { API } from "../config";
import axios from "axios";
import {
  Send, Loader2, Sparkles, Bot, Zap, ChevronRight, 
  Info, History, Settings, ArrowLeft
} from "lucide-react";

const UniversalAssistant = () => {
  const { user, token } = useAuth();
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "👋 Hi! I'm the NEXUS Universal AI Assistant. I can help you with **anything** - just ask!\n\n💡 I can:\n- Generate images, videos, or music\n- Run multi-agent workflows\n- Analyze code and provide development tools\n- Process payments and send notifications\n- Discover AI tools from GitHub\n- And 40+ other specialized services!\n\nWhat can I help you with today?",
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId] = useState(`session_${Date.now()}`);
  const [showServices, setShowServices] = useState(false);
  const [services, setServices] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load available services on mount
  useEffect(() => {
    loadServices();
  }, []);

  const loadServices = async () => {
    try {
      const res = await axios.get(`${API}/universal/services`);
      setServices(res.data);
    } catch (err) {
      console.error("Failed to load services:", err);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    
    // Add user message to UI
    const userMsg = {
      role: "user",
      content: userMessage,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const res = await axios.post(
        `${API}/universal/process`,
        {
          message: userMessage,
          session_id: sessionId
        },
        { headers }
      );

      // Add assistant response
      const assistantMsg = {
        role: "assistant",
        content: res.data.response,
        timestamp: new Date(),
        metadata: res.data.metadata,
        routed_to: res.data.routed_to,
        service_used: res.data.service_used
      };
      
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err) {
      console.error("Error sending message:", err);
      const errorMsg = {
        role: "assistant",
        content: `❌ Sorry, I encountered an error: ${err.response?.data?.detail || err.message}`,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickPrompts = [
    { icon: "🎨", text: "Generate an image of a futuristic city", category: "image" },
    { icon: "🎵", text: "Create a lo-fi beat", category: "music" },
    { icon: "🎬", text: "Generate a short video", category: "video" },
    { icon: "🤖", text: "Run a multi-agent research team", category: "agents" },
    { icon: "💳", text: "Process a payment", category: "business" },
    { icon: "🔍", text: "Discover AI tools on GitHub", category: "tools" },
  ];

  return (
    <div className="min-h-screen pt-32 pb-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="font-rajdhani text-4xl md:text-5xl font-bold mb-3">
            Universal AI Assistant
          </h1>
          <p className="text-white/60 text-lg max-w-2xl mx-auto">
            One interface. 44+ specialized services. Anything you need.
          </p>
          
          {/* Quick Actions */}
          <div className="flex gap-3 justify-center mt-6">
            <button
              onClick={() => setShowServices(!showServices)}
              className="btn-secondary px-4 py-2 rounded-lg text-sm flex items-center gap-2"
            >
              <Info className="w-4 h-4" />
              {showServices ? "Hide" : "Show"} Services
            </button>
          </div>
        </motion.div>

        {/* Services List (Collapsible) */}
        <AnimatePresence>
          {showServices && services && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="glass rounded-2xl p-6 mb-6 overflow-hidden"
            >
              <h3 className="font-rajdhani text-xl font-bold mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5 text-cyan-400" />
                Available Services ({services.total_services})
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-96 overflow-y-auto">
                {Object.entries(services.services).map(([intent, info]) => (
                  <div
                    key={intent}
                    className="bg-white/5 rounded-lg p-3 border border-white/10 hover:border-cyan-500/50 transition-colors"
                  >
                    <div className="text-sm font-semibold text-cyan-400 mb-1">
                      {info.service}
                    </div>
                    <div className="text-xs text-white/60">
                      {info.description}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Chat Container */}
        <div className="glass rounded-2xl overflow-hidden">
          {/* Messages */}
          <div className="h-[600px] overflow-y-auto p-6 space-y-6">
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div className={`flex gap-3 max-w-[80%] ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
                  {/* Avatar */}
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                    msg.role === "user"
                      ? "bg-gradient-to-br from-cyan-500 to-purple-600"
                      : "bg-white/10 border border-white/20"
                  }`}>
                    {msg.role === "user" ? (
                      user ? (
                        <img
                          src={user.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.username}`}
                          alt=""
                          className="w-full h-full rounded-xl object-cover"
                        />
                      ) : (
                        <span className="text-sm font-bold">U</span>
                      )
                    ) : (
                      <Bot className="w-5 h-5 text-cyan-400" />
                    )}
                  </div>

                  {/* Message Content */}
                  <div className="flex-1 min-w-0">
                    <div className={`p-4 rounded-xl ${
                      msg.role === "user"
                        ? "bg-gradient-to-br from-cyan-500/20 to-purple-500/20 border border-cyan-500/30"
                        : msg.isError
                        ? "bg-red-500/10 border border-red-500/30"
                        : "bg-white/5 border border-white/10"
                    }`}>
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      
                      {/* Metadata */}
                      {msg.metadata && (
                        <div className="mt-3 pt-3 border-t border-white/10">
                          <div className="flex flex-wrap gap-2 text-xs">
                            {msg.routed_to && (
                              <span className="px-2 py-1 rounded-md bg-cyan-500/20 text-cyan-400">
                                Intent: {msg.routed_to}
                              </span>
                            )}
                            {msg.service_used && (
                              <span className="px-2 py-1 rounded-md bg-purple-500/20 text-purple-400">
                                Service: {msg.service_used}
                              </span>
                            )}
                            {msg.metadata.confidence && (
                              <span className="px-2 py-1 rounded-md bg-white/10 text-white/60">
                                Confidence: {(msg.metadata.confidence * 100).toFixed(0)}%
                              </span>
                            )}
                          </div>
                          {msg.metadata.reasoning && (
                            <p className="text-xs text-white/40 mt-2">
                              💡 {msg.metadata.reasoning}
                            </p>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="text-xs text-white/30 mt-1 px-1">
                      {msg.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}

            {loading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start"
              >
                <div className="flex gap-3">
                  <div className="w-10 h-10 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center">
                    <Bot className="w-5 h-5 text-cyan-400" />
                  </div>
                  <div className="bg-white/5 p-4 rounded-xl border border-white/10">
                    <Loader2 className="w-5 h-5 animate-spin text-cyan-400" />
                  </div>
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Prompts */}
          {messages.length === 1 && (
            <div className="px-6 pb-4">
              <p className="text-xs text-white/40 mb-3">Quick Prompts:</p>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {quickPrompts.map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(prompt.text)}
                    className="text-left px-3 py-2 rounded-lg bg-white/5 border border-white/10 hover:border-cyan-500/50 transition-colors text-sm"
                  >
                    <span className="mr-2">{prompt.icon}</span>
                    {prompt.text}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="border-t border-white/10 p-6">
            <div className="flex gap-3">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything... (Shift+Enter for new line)"
                rows={1}
                className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:border-cyan-500/50 focus:outline-none text-white placeholder:text-white/30 resize-none"
                style={{ minHeight: "52px", maxHeight: "120px" }}
              />
              <button
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                className="px-6 py-3 bg-gradient-to-br from-cyan-500 to-purple-600 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-cyan-500/25 transition-all flex items-center gap-2"
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin text-white" />
                ) : (
                  <Send className="w-5 h-5 text-white" />
                )}
              </button>
            </div>
            <p className="text-xs text-white/30 mt-2">
              Powered by GPT-5.1 • Routing to 44+ specialized services
            </p>
          </div>
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-cyan-400" />
              </div>
              <h3 className="font-semibold">Smart Routing</h3>
            </div>
            <p className="text-sm text-white/60">
              AI-powered intent classification routes your request to the perfect service
            </p>
          </div>

          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                <Zap className="w-5 h-5 text-purple-400" />
              </div>
              <h3 className="font-semibold">44+ Services</h3>
            </div>
            <p className="text-sm text-white/60">
              Access to all NEXUS hybrid services through one unified interface
            </p>
          </div>

          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                <History className="w-5 h-5 text-green-400" />
              </div>
              <h3 className="font-semibold">Context Aware</h3>
            </div>
            <p className="text-sm text-white/60">
              Maintains conversation history and learns from your requests
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UniversalAssistant;
