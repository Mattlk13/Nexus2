import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { useAuth } from "../App";
import { API } from "../config";
import axios from "axios";
import {
  Terminal, Code, FolderOpen, Globe, Zap, Play, X, 
  Plus, Trash2, RefreshCw, Maximize2, Minimize2, Settings,
  FileText, Save, Download, Upload, Eye, Monitor
} from "lucide-react";

const AgentWorkspace = () => {
  const { user, token } = useAuth();
  const [sandboxes, setSandboxes] = useState([]);
  const [activeSandbox, setActiveSandbox] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeView, setActiveView] = useState("terminal"); // terminal, editor, browser, files
  const [terminalOutput, setTerminalOutput] = useState([]);
  const [command, setCommand] = useState("");
  const [files, setFiles] = useState([]);
  const [editorContent, setEditorContent] = useState("");
  const [currentFile, setCurrentFile] = useState(null);
  const terminalRef = useRef(null);

  useEffect(() => {
    loadSandboxes();
  }, []);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [terminalOutput]);

  const loadSandboxes = async () => {
    try {
      const res = await axios.get(`${API}/hybrid/aio-sandbox/list`);
      setSandboxes(res.data.sandboxes || []);
      
      // If no sandboxes, create default one
      if (res.data.sandboxes.length === 0) {
        await createSandbox();
      } else {
        setActiveSandbox(res.data.sandboxes[0]);
      }
    } catch (err) {
      console.error("Failed to load sandboxes:", err);
    }
  };

  const createSandbox = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/hybrid/aio-sandbox/create`, {
        sandbox_id: `sandbox_${Date.now()}`,
        name: `Workspace ${sandboxes.length + 1}`,
        environment: {
          NODE_ENV: "development",
          PYTHON_VERSION: "3.11"
        }
      });
      
      await loadSandboxes();
      setActiveSandbox(res.data.sandbox);
      addToTerminal("✅ Sandbox created successfully", "success");
    } catch (err) {
      console.error("Failed to create sandbox:", err);
      addToTerminal(`❌ Error: ${err.message}`, "error");
    } finally {
      setLoading(false);
    }
  };

  const deleteSandbox = async (sandboxId) => {
    if (!confirm("Delete this sandbox? All data will be lost.")) return;
    
    try {
      await axios.delete(`${API}/hybrid/aio-sandbox/${sandboxId}`);
      await loadSandboxes();
      addToTerminal(`✅ Sandbox ${sandboxId} deleted`, "success");
    } catch (err) {
      console.error("Failed to delete sandbox:", err);
    }
  };

  const executeCommand = async () => {
    if (!command.trim() || !activeSandbox) return;

    const cmd = command.trim();
    setCommand("");
    addToTerminal(`$ ${cmd}`, "command");

    try {
      const res = await axios.post(`${API}/hybrid/aio-sandbox/${activeSandbox.id}/shell`, {
        command: cmd,
        cwd: activeSandbox.file_system.home
      });

      addToTerminal(res.data.output, res.data.exit_code === 0 ? "output" : "error");
    } catch (err) {
      addToTerminal(`Error: ${err.response?.data?.detail || err.message}`, "error");
    }
  };

  const addToTerminal = (text, type = "output") => {
    setTerminalOutput(prev => [...prev, { text, type, timestamp: new Date() }]);
  };

  const loadFiles = async () => {
    if (!activeSandbox) return;

    try {
      const res = await axios.post(`${API}/hybrid/aio-sandbox/${activeSandbox.id}/file`, {
        operation: "list",
        path: activeSandbox.file_system.home
      });

      setFiles(res.data.files || []);
    } catch (err) {
      console.error("Failed to load files:", err);
    }
  };

  const openFile = async (file) => {
    if (!activeSandbox || file.type === "directory") return;

    try {
      const res = await axios.post(`${API}/hybrid/aio-sandbox/${activeSandbox.id}/file`, {
        operation: "read",
        path: `${activeSandbox.file_system.home}/${file.name}`
      });

      setEditorContent(res.data.content || "");
      setCurrentFile(file);
      setActiveView("editor");
    } catch (err) {
      console.error("Failed to open file:", err);
    }
  };

  const saveFile = async () => {
    if (!activeSandbox || !currentFile) return;

    try {
      await axios.post(`${API}/hybrid/aio-sandbox/${activeSandbox.id}/file`, {
        operation: "write",
        path: `${activeSandbox.file_system.home}/${currentFile.name}`,
        content: editorContent
      });

      addToTerminal(`✅ Saved ${currentFile.name}`, "success");
    } catch (err) {
      addToTerminal(`❌ Failed to save: ${err.message}`, "error");
    }
  };

  useEffect(() => {
    if (activeView === "files" && activeSandbox) {
      loadFiles();
    }
  }, [activeView, activeSandbox]);

  const viewTabs = [
    { id: "terminal", icon: Terminal, label: "Terminal" },
    { id: "editor", icon: Code, label: "Code Editor" },
    { id: "files", icon: FolderOpen, label: "Files" },
    { id: "browser", icon: Globe, label: "Browser" },
  ];

  return (
    <div className="min-h-screen pt-32 pb-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="font-rajdhani text-4xl font-bold mb-2">
                Agent Workspace
              </h1>
              <p className="text-white/60">
                AIO Sandbox: Browser, Terminal, Editor, Files - All in one environment
              </p>
            </div>
            
            <button
              onClick={createSandbox}
              disabled={loading}
              className="btn-primary px-4 py-2 rounded-lg flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              New Sandbox
            </button>
          </div>

          {/* Sandbox Selector */}
          <div className="flex gap-2 overflow-x-auto pb-2">
            {sandboxes.map((sandbox) => (
              <button
                key={sandbox.id}
                onClick={() => setActiveSandbox(sandbox)}
                className={`px-4 py-2 rounded-lg flex items-center gap-2 flex-shrink-0 transition-colors ${
                  activeSandbox?.id === sandbox.id
                    ? "bg-cyan-500/20 border border-cyan-500/50"
                    : "bg-white/5 border border-white/10 hover:border-white/20"
                }`}
              >
                <Monitor className="w-4 h-4" />
                <span className="text-sm">{sandbox.name}</span>
                {sandboxes.length > 1 && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteSandbox(sandbox.id);
                    }}
                    className="p-1 hover:bg-red-500/20 rounded"
                  >
                    <X className="w-3 h-3" />
                  </button>
                )}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Main Workspace */}
        {activeSandbox && (
          <div className="glass rounded-2xl overflow-hidden">
            {/* View Tabs */}
            <div className="flex items-center gap-1 p-2 border-b border-white/10">
              {viewTabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveView(tab.id)}
                  className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
                    activeView === tab.id
                      ? "bg-cyan-500/20 text-cyan-400"
                      : "text-white/60 hover:text-white hover:bg-white/5"
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  <span className="text-sm">{tab.label}</span>
                </button>
              ))}
              
              <div className="flex-1" />
              
              {activeView === "editor" && currentFile && (
                <button
                  onClick={saveFile}
                  className="px-3 py-2 bg-green-500/20 text-green-400 rounded-lg flex items-center gap-2 text-sm"
                >
                  <Save className="w-4 h-4" />
                  Save
                </button>
              )}
            </div>

            {/* Content Area */}
            <div className="h-[600px] overflow-hidden">
              {/* Terminal View */}
              {activeView === "terminal" && (
                <div className="h-full flex flex-col">
                  <div
                    ref={terminalRef}
                    className="flex-1 overflow-y-auto p-4 font-mono text-sm bg-black/40"
                  >
                    {terminalOutput.map((line, i) => (
                      <div
                        key={i}
                        className={`mb-1 ${
                          line.type === "command"
                            ? "text-cyan-400"
                            : line.type === "error"
                            ? "text-red-400"
                            : line.type === "success"
                            ? "text-green-400"
                            : "text-white/80"
                        }`}
                      >
                        {line.text}
                      </div>
                    ))}
                  </div>
                  
                  <div className="p-4 border-t border-white/10 flex items-center gap-2">
                    <span className="text-cyan-400 font-mono">$</span>
                    <input
                      type="text"
                      value={command}
                      onChange={(e) => setCommand(e.target.value)}
                      onKeyPress={(e) => e.key === "Enter" && executeCommand()}
                      placeholder="Enter command..."
                      className="flex-1 bg-transparent border-none focus:outline-none text-white font-mono"
                    />
                    <button
                      onClick={executeCommand}
                      className="px-3 py-1 bg-cyan-500/20 text-cyan-400 rounded hover:bg-cyan-500/30"
                    >
                      <Play className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}

              {/* Code Editor View */}
              {activeView === "editor" && (
                <div className="h-full flex flex-col">
                  {currentFile ? (
                    <>
                      <div className="p-2 border-b border-white/10 flex items-center gap-2 text-sm">
                        <FileText className="w-4 h-4 text-cyan-400" />
                        <span>{currentFile.name}</span>
                      </div>
                      <textarea
                        value={editorContent}
                        onChange={(e) => setEditorContent(e.target.value)}
                        className="flex-1 p-4 bg-black/40 text-white font-mono text-sm resize-none focus:outline-none"
                        spellCheck="false"
                      />
                    </>
                  ) : (
                    <div className="flex-1 flex items-center justify-center text-white/40">
                      <div className="text-center">
                        <Code className="w-12 h-12 mx-auto mb-3 opacity-50" />
                        <p>No file open</p>
                        <p className="text-sm mt-1">Select a file from the Files tab</p>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Files View */}
              {activeView === "files" && (
                <div className="h-full overflow-y-auto p-4">
                  <div className="grid grid-cols-1 gap-2">
                    {files.map((file, i) => (
                      <button
                        key={i}
                        onClick={() => openFile(file)}
                        className="p-3 bg-white/5 hover:bg-white/10 rounded-lg text-left flex items-center gap-3 transition-colors"
                      >
                        {file.type === "directory" ? (
                          <FolderOpen className="w-5 h-5 text-yellow-400" />
                        ) : (
                          <FileText className="w-5 h-5 text-cyan-400" />
                        )}
                        <div className="flex-1">
                          <div className="font-medium">{file.name}</div>
                          {file.size && (
                            <div className="text-xs text-white/40">
                              {(file.size / 1024).toFixed(1)} KB
                            </div>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Browser View */}
              {activeView === "browser" && (
                <div className="h-full flex items-center justify-center bg-black/40">
                  <div className="text-center text-white/60">
                    <Globe className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p className="text-lg mb-2">Browser Preview</p>
                    <p className="text-sm">
                      VNC interface at: <code className="text-cyan-400">/sandbox/{activeSandbox.id}/vnc/index.html</code>
                    </p>
                    <p className="text-sm mt-2">
                      VSCode Server at: <code className="text-cyan-400">/sandbox/{activeSandbox.id}/code-server/</code>
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <Terminal className="w-5 h-5 text-cyan-400" />
              <h3 className="font-semibold text-sm">Shell Access</h3>
            </div>
            <p className="text-xs text-white/60">
              WebSocket terminal with full bash capabilities
            </p>
          </div>

          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <Code className="w-5 h-5 text-purple-400" />
              <h3 className="font-semibold text-sm">VSCode Server</h3>
            </div>
            <p className="text-xs text-white/60">
              Full IDE experience in the browser
            </p>
          </div>

          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <FolderOpen className="w-5 h-5 text-yellow-400" />
              <h3 className="font-semibold text-sm">File System</h3>
            </div>
            <p className="text-xs text-white/60">
              Unified file system across all components
            </p>
          </div>

          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <Zap className="w-5 h-5 text-green-400" />
              <h3 className="font-semibold text-sm">MCP Hub</h3>
            </div>
            <p className="text-xs text-white/60">
              Aggregated services for AI agents
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentWorkspace;
