import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "../App";
import { API } from "../config";
import axios from "axios";
import {
  Video, Film, Play, Download, Upload, Wand2, Sparkles,
  Camera, Image, Music, Mic, FileVideo, Loader2, Check, X
} from "lucide-react";

const OmmaVideoGenerator = () => {
  const { user, token } = useAuth();
  const [prompt, setPrompt] = useState("");
  const [videoStyle, setVideoStyle] = useState("cinematic");
  const [duration, setDuration] = useState(5);
  const [loading, setLoading] = useState(false);
  const [generatedVideo, setGeneratedVideo] = useState(null);

  const videoStyles = [
    { id: "cinematic", name: "Cinematic", icon: Film },
    { id: "anime", name: "Anime", icon: Sparkles },
    { id: "realistic", name: "Realistic", icon: Camera },
    { id: "abstract", name: "Abstract", icon: Wand2 },
  ];

  const durations = [3, 5, 10, 15, 30];

  const generateVideo = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const res = await axios.post(
        `${API}/v2/hybrid/sora_video/generate`,
        {
          prompt: prompt,
          style: videoStyle,
          duration: duration,
          resolution: "1080p",
          fps: 24
        },
        { headers }
      );

      setGeneratedVideo(res.data);
    } catch (err) {
      console.error("Video generation error:", err);
      alert(`Error: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

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
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
              <Video className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="font-rajdhani text-4xl md:text-5xl font-bold mb-3">
            OMMA Video Generator
          </h1>
          <p className="text-white/60 text-lg">
            AI-powered video generation using Sora 2
          </p>
        </motion.div>

        {/* Generation Interface */}
        <div className="glass rounded-2xl p-8 mb-6">
          {/* Prompt Input */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-2">
              Video Prompt
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the video you want to generate... (e.g., 'A serene lake at sunset with mountains in the background')"
              rows={4}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:border-purple-500/50 focus:outline-none text-white placeholder:text-white/30 resize-none"
            />
          </div>

          {/* Style Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-3">
              Video Style
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {videoStyles.map((style) => (
                <button
                  key={style.id}
                  onClick={() => setVideoStyle(style.id)}
                  className={`p-4 rounded-xl border-2 transition-all ${
                    videoStyle === style.id
                      ? "border-purple-500 bg-purple-500/20"
                      : "border-white/10 bg-white/5 hover:border-white/20"
                  }`}
                >
                  <style.icon className="w-6 h-6 mx-auto mb-2" />
                  <div className="text-sm font-medium">{style.name}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Duration Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium mb-3">
              Duration (seconds)
            </label>
            <div className="flex gap-2">
              {durations.map((dur) => (
                <button
                  key={dur}
                  onClick={() => setDuration(dur)}
                  className={`px-4 py-2 rounded-lg transition-all ${
                    duration === dur
                      ? "bg-purple-500 text-white"
                      : "bg-white/5 hover:bg-white/10"
                  }`}
                >
                  {dur}s
                </button>
              ))}
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={generateVideo}
            disabled={loading || !prompt.trim()}
            className="w-full px-6 py-4 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-purple-500/25 transition-all flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Generating Video...
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Generate Video
              </>
            )}
          </button>
        </div>

        {/* Generated Video Display */}
        <AnimatePresence>
          {generatedVideo && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-semibold">Generated Video</h3>
                <button
                  onClick={() => setGeneratedVideo(null)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Video Player */}
              <div className="aspect-video bg-black rounded-xl overflow-hidden mb-4">
                {generatedVideo.video_url ? (
                  <video
                    src={generatedVideo.video_url}
                    controls
                    className="w-full h-full"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-white/40">
                    <FileVideo className="w-16 h-16" />
                  </div>
                )}
              </div>

              {/* Video Info */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="text-center p-3 bg-white/5 rounded-lg">
                  <div className="text-xs text-white/40 mb-1">Style</div>
                  <div className="font-medium capitalize">{videoStyle}</div>
                </div>
                <div className="text-center p-3 bg-white/5 rounded-lg">
                  <div className="text-xs text-white/40 mb-1">Duration</div>
                  <div className="font-medium">{duration}s</div>
                </div>
                <div className="text-center p-3 bg-white/5 rounded-lg">
                  <div className="text-xs text-white/40 mb-1">Resolution</div>
                  <div className="font-medium">1080p</div>
                </div>
                <div className="text-center p-3 bg-white/5 rounded-lg">
                  <div className="text-xs text-white/40 mb-1">FPS</div>
                  <div className="font-medium">24</div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3">
                <button className="flex-1 px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors flex items-center justify-center gap-2">
                  <Download className="w-4 h-4" />
                  Download
                </button>
                <button className="flex-1 px-4 py-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors flex items-center justify-center gap-2">
                  <Upload className="w-4 h-4" />
                  Share
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                <Film className="w-5 h-5 text-purple-400" />
              </div>
              <h3 className="font-semibold text-sm">Sora 2 Powered</h3>
            </div>
            <p className="text-xs text-white/60">
              State-of-the-art AI video generation
            </p>
          </div>

          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-pink-500/20 flex items-center justify-center">
                <Wand2 className="w-5 h-5 text-pink-400" />
              </div>
              <h3 className="font-semibold text-sm">Multiple Styles</h3>
            </div>
            <p className="text-xs text-white/60">
              Cinematic, anime, realistic, and abstract
            </p>
          </div>

          <div className="glass rounded-xl p-4">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-cyan-400" />
              </div>
              <h3 className="font-semibold text-sm">High Quality</h3>
            </div>
            <p className="text-xs text-white/60">
              1080p resolution at 24fps
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OmmaVideoGenerator;
