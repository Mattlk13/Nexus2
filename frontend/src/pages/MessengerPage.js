import React, { useState, useEffect } from 'react';
import { MessageCircle, Video, Phone, Send, Users, Plus } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const MessengerPage = () => {
  const [rooms, setRooms] = useState([]);
  const [activeRoom, setActiveRoom] = useState(null);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRooms();
  }, []);

  const fetchRooms = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setRooms([]);
        setLoading(false);
        return;
      }
      
      const response = await axios.get(`${API_URL}/api/messenger/rooms`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setRooms(response.data.rooms || []);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch rooms:', err);
      setRooms([]);
      setLoading(false);
    }
  };

  const createRoom = async () => {
    const roomName = prompt('Enter room name:');
    if (!roomName) return;

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/api/messenger/rooms`,
        { name: roomName },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setRooms([...rooms, response.data]);
      alert('Room created!');
    } catch (err) {
      alert('Failed to create room: ' + (err.response?.data?.detail || err.message));
    }
  };

  const sendMessage = async () => {
    if (!message.trim() || !activeRoom) return;

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/messenger/rooms/${activeRoom}/messages`,
        { content: message },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage('');
      // In a real app, we'd update messages via WebSocket
      alert('Message sent! (Real-time messaging coming soon)');
    } catch (err) {
      alert('Failed to send message: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white flex">
      {/* Sidebar */}
      <div className="w-80 bg-gray-800 border-r border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
            HyperMessenger
          </h1>
          <p className="text-sm text-gray-400 mt-1">Matrix + Jitsi Integration</p>
        </div>

        <div className="p-4">
          <button
            onClick={createRoom}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-700 hover:to-purple-700 rounded-lg transition-all"
          >
            <Plus className="w-5 h-5" />
            Create Room
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="p-4 space-y-2">
            <h3 className="text-sm font-semibold text-gray-400 mb-3">ROOMS</h3>
            {loading ? (
              <p className="text-gray-500 text-sm">Loading rooms...</p>
            ) : rooms.length === 0 ? (
              <p className="text-gray-500 text-sm">No rooms yet. Create one!</p>
            ) : (
              rooms.map((room) => (
                <button
                  key={room.id}
                  onClick={() => setActiveRoom(room.id)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    activeRoom === room.id
                      ? 'bg-cyan-600/20 border border-cyan-500/50'
                      : 'bg-gray-700/50 hover:bg-gray-700 border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-cyan-500/20 rounded-lg">
                      <MessageCircle className="w-4 h-4 text-cyan-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{room.name}</p>
                      <p className="text-xs text-gray-400">Click to open</p>
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {activeRoom ? (
          <>
            {/* Chat Header */}
            <div className="p-4 border-b border-gray-700 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-cyan-500/20 rounded-lg">
                  <MessageCircle className="w-6 h-6 text-cyan-400" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold">
                    {rooms.find(r => r.id === activeRoom)?.name || 'Room'}
                  </h2>
                  <p className="text-sm text-gray-400">Active room</p>
                </div>
              </div>
              <div className="flex gap-2">
                <button className="p-3 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors">
                  <Phone className="w-5 h-5 text-green-400" />
                </button>
                <button className="p-3 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors">
                  <Video className="w-5 h-5 text-blue-400" />
                </button>
              </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 p-6 overflow-y-auto bg-gray-900/50">
              <div className="max-w-4xl mx-auto">
                <div className="text-center py-12">
                  <MessageCircle className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400">Send your first message!</p>
                  <p className="text-sm text-gray-500 mt-2">Real-time messaging with Matrix integration</p>
                </div>
              </div>
            </div>

            {/* Message Input */}
            <div className="p-4 border-t border-gray-700">
              <div className="max-w-4xl mx-auto flex gap-3">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Type a message..."
                  className="flex-1 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg focus:outline-none focus:border-cyan-500 text-white placeholder-gray-500"
                />
                <button
                  onClick={sendMessage}
                  disabled={!message.trim()}
                  className="px-6 py-3 bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-700 hover:to-purple-700 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <MessageCircle className="w-20 h-20 text-gray-700 mx-auto mb-4" />
              <h3 className="text-2xl font-semibold text-gray-300 mb-2">Select a room</h3>
              <p className="text-gray-500">Choose a room from the sidebar or create a new one</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessengerPage;