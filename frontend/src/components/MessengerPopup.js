import React, { useState, useEffect } from 'react';
import { MessageCircle, X, Minimize2, Maximize2, Video, Phone, GamepadIcon, Palette, Send, Circle } from 'lucide-react';
import axios from 'axios';
import { useAuth, API } from '../App';

const MessengerPopup = () => {
  const { token, user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [activeChat, setActiveChat] = useState(null);
  const [message, setMessage] = useState('');
  const [rooms, setRooms] = useState([]);
  const [onlineFriends, setOnlineFriends] = useState([]);
  const [bgTheme, setBgTheme] = useState('default');
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    if (isOpen && user) {
      fetchRooms();
      fetchOnlineFriends();
      // Real-time updates every 5 seconds
      const interval = setInterval(() => {
        fetchRooms();
        fetchOnlineFriends();
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [isOpen, user]);

  const fetchRooms = async () => {
    try {
      const response = await axios.get(`${API}/api/messenger/rooms`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setRooms(response.data.rooms || []);
    } catch (err) {
      console.error('Failed to fetch rooms:', err);
    }
  };

  const fetchOnlineFriends = async () => {
    try {
      const response = await axios.get(`${API}/api/messenger/online-friends`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setOnlineFriends(response.data.online_friends || []);
    } catch (err) {
      setOnlineFriends([{ id: '1', name: 'Demo Friend', online: true }]);
    }
  };

  const sendMessage = async () => {
    if (!message.trim() || !activeChat) return;
    
    try {
      await axios.post(
        `${API}/api/messenger/rooms/${activeChat}/messages`,
        { content: message },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage('');
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  const bgThemes = {
    default: 'bg-gradient-to-br from-gray-900 to-gray-800',
    ocean: 'bg-gradient-to-br from-blue-900 to-cyan-900',
    sunset: 'bg-gradient-to-br from-orange-900 to-pink-900',
    forest: 'bg-gradient-to-br from-green-900 to-emerald-900',
    galaxy: 'bg-gradient-to-br from-purple-900 to-indigo-900'
  };

  if (!user) return null;

  return (
    <>
      {/* Messenger Button - Always Visible */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 w-16 h-16 bg-gradient-to-br from-cyan-500 to-purple-500 rounded-full shadow-2xl flex items-center justify-center hover:scale-110 transition-transform"
      >
        <MessageCircle className="w-7 h-7 text-white" />
        {onlineFriends.filter(f => f.online).length > 0 && (
          <span className="absolute -top-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-2 border-black flex items-center justify-center text-xs font-bold">
            {onlineFriends.filter(f => f.online).length}
          </span>
        )}
      </button>

      {/* Messenger Popup */}
      {isOpen && (
        <div
          className={`fixed z-50 shadow-2xl border border-white/20 rounded-2xl overflow-hidden transition-all ${
            isMinimized ? 'bottom-6 right-24 w-80 h-16' : 'bottom-6 right-24 w-[450px] h-[600px]'
          }`}
        >
          {/* Header */}
          <div className={`${bgThemes[bgTheme]} p-4 flex items-center justify-between border-b border-white/10`}>
            <div className="flex items-center gap-3">
              <MessageCircle className="w-5 h-5 text-cyan-400" />
              <h3 className="font-bold text-white">
                {activeChat ? 'Chat' : 'Messenger'}
              </h3>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-2 hover:bg-white/10 rounded-lg transition-all"
              >
                <Palette className="w-4 h-4 text-white" />
              </button>
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className="p-2 hover:bg-white/10 rounded-lg transition-all"
              >
                {isMinimized ? <Maximize2 className="w-4 h-4 text-white" /> : <Minimize2 className="w-4 h-4 text-white" />}
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-white/10 rounded-lg transition-all"
              >
                <X className="w-4 h-4 text-white" />
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              {/* Background Theme Selector */}
              {showSettings && (
                <div className="p-4 bg-black/40 border-b border-white/10">
                  <p className="text-xs text-gray-400 mb-2">Background Theme</p>
                  <div className="flex gap-2">
                    {Object.keys(bgThemes).map((theme) => (
                      <button
                        key={theme}
                        onClick={() => setBgTheme(theme)}
                        className={`flex-1 h-8 ${bgThemes[theme]} rounded-lg border-2 ${
                          bgTheme === theme ? 'border-cyan-400' : 'border-transparent'
                        } transition-all`}
                      />
                    ))}
                  </div>
                </div>
              )}

              {activeChat ? (
                /* Chat View */
                <div className={`flex flex-col h-[calc(100%-64px)] ${bgThemes[bgTheme]}`}>
                  {/* Chat Header */}
                  <div className="p-4 bg-black/40 border-b border-white/10 flex items-center justify-between">
                    <button
                      onClick={() => setActiveChat(null)}
                      className="text-cyan-400 hover:text-cyan-300 text-sm font-semibold"
                    >
                      ← Back
                    </button>
                    <div className="flex gap-2">
                      <button className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-all">
                        <Phone className="w-4 h-4 text-green-400" />
                      </button>
                      <button className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-all">
                        <Video className="w-4 h-4 text-blue-400" />
                      </button>
                      <button className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-all">
                        <GamepadIcon className="w-4 h-4 text-purple-400" />
                      </button>
                    </div>
                  </div>

                  {/* Messages */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-3">
                    <div className="bg-black/40 backdrop-blur-sm rounded-2xl p-3 max-w-[80%]">
                      <p className="text-white text-sm">Hey! How are you?</p>
                      <p className="text-xs text-gray-400 mt-1">2:30 PM</p>
                    </div>
                    <div className="bg-gradient-to-br from-cyan-600 to-purple-600 rounded-2xl p-3 max-w-[80%] ml-auto">
                      <p className="text-white text-sm">I'm good! Working on some music.</p>
                      <p className="text-xs text-cyan-100 mt-1">2:31 PM</p>
                    </div>
                  </div>

                  {/* Message Input */}
                  <div className="p-4 bg-black/40 border-t border-white/10">
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                        placeholder="Type a message..."
                        className="flex-1 bg-white/10 border border-white/20 rounded-xl px-4 py-2 text-sm text-white placeholder-gray-400 focus:outline-none focus:border-cyan-400 transition-all"
                      />
                      <button
                        onClick={sendMessage}
                        className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-purple-600 hover:from-cyan-700 hover:to-purple-700 rounded-xl transition-all"
                      >
                        <Send className="w-4 h-4 text-white" />
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                /* Contacts List */
                <div className="h-[calc(100%-64px)] bg-gray-900 overflow-y-auto">
                  {/* Online Friends */}
                  <div className="p-4">
                    <h4 className="text-xs font-semibold text-gray-400 mb-3">ONLINE FRIENDS ({onlineFriends.filter(f => f.online).length})</h4>
                    <div className="space-y-2">
                      {onlineFriends.filter(f => f.online).map((friend) => (
                        <button
                          key={friend.id}
                          onClick={() => setActiveChat(friend.id)}
                          className="w-full flex items-center gap-3 p-3 hover:bg-white/5 rounded-xl transition-all"
                        >
                          <div className="relative">
                            <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-purple-500 rounded-full flex items-center justify-center font-bold text-sm">
                              {friend.name.charAt(0)}
                            </div>
                            <Circle className="absolute -bottom-1 -right-1 w-4 h-4 fill-green-500 text-green-500" />
                          </div>
                          <div className="flex-1 text-left">
                            <p className="font-semibold text-white text-sm">{friend.name}</p>
                            <p className="text-xs text-green-400">Active now</p>
                          </div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Recent Chats */}
                  <div className="p-4 border-t border-white/10">
                    <h4 className="text-xs font-semibold text-gray-400 mb-3">RECENT CHATS</h4>
                    <div className="space-y-2">
                      {rooms.map((room) => (
                        <button
                          key={room.id}
                          onClick={() => setActiveChat(room.id)}
                          className="w-full flex items-center gap-3 p-3 hover:bg-white/5 rounded-xl transition-all"
                        >
                          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-full flex items-center justify-center">
                            <MessageCircle className="w-5 h-5 text-white" />
                          </div>
                          <div className="flex-1 text-left">
                            <p className="font-semibold text-white text-sm">{room.name}</p>
                            <p className="text-xs text-gray-400 truncate">Click to open chat</p>
                          </div>
                        </button>
                      ))}
                      {rooms.length === 0 && (
                        <p className="text-sm text-gray-500 text-center py-4">No recent chats</p>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </>
  );
};

export default MessengerPopup;