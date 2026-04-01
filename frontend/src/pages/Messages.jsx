import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Send, Search, MoreVertical, Phone, Video, Paperclip } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const Messages = () => {
  const [conversations, setConversations] = useState([]);
  const [activeChat, setActiveChat] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [ws, setWs] = useState(null);
  const [user] = useState({ id: 'demo-user', username: 'You' });
  const messagesEndRef = useRef(null);

  // Mock conversations
  useEffect(() => {
    const mockConversations = [
      { id: 1, name: 'Alice Johnson', avatar: '👩', lastMessage: 'Hey! How are you?', time: '2m ago', unread: 2, online: true },
      { id: 2, name: 'Bob Smith', avatar: '👨', lastMessage: 'Thanks for the help!', time: '1h ago', unread: 0, online: false },
      { id: 3, name: 'Carol Davis', avatar: '👩‍💼', lastMessage: 'See you tomorrow', time: '3h ago', unread: 0, online: true },
      { id: 4, name: 'David Wilson', avatar: '🧑', lastMessage: 'Got it!', time: '1d ago', unread: 1, online: false },
    ];
    setConversations(mockConversations);
  }, []);

  // WebSocket connection
  useEffect(() => {
    const websocket = new WebSocket(`wss://${window.location.host.replace('https://', '')}/api/ws/${user.id}`);
    
    websocket.onopen = () => {
      console.log('WebSocket connected');
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'new_message') {
        setMessages(prev => [...prev, data.message]);
        scrollToBottom();
      } else if (data.type === 'user_typing') {
        // Show typing indicator
      }
    };

    setWs(websocket);
    return () => websocket.close();
  }, [user.id]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const selectChat = (conversation) => {
    setActiveChat(conversation);
    // Load messages for this conversation
    const mockMessages = [
      { id: 1, from_user_id: conversation.id, to_user_id: user.id, content: 'Hey there!', created_at: new Date(Date.now() - 3600000) },
      { id: 2, from_user_id: user.id, to_user_id: conversation.id, content: 'Hi! How can I help?', created_at: new Date(Date.now() - 3000000) },
      { id: 3, from_user_id: conversation.id, to_user_id: user.id, content: conversation.lastMessage, created_at: new Date() },
    ];
    setMessages(mockMessages);
  };

  const sendMessage = () => {
    if (!newMessage.trim() || !activeChat) return;

    const message = {
      id: Date.now(),
      from_user_id: user.id,
      to_user_id: activeChat.id,
      content: newMessage,
      created_at: new Date()
    };

    // Send via WebSocket
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'chat_message',
        to_user_id: activeChat.id,
        content: newMessage
      }));
    }

    setMessages([...messages, message]);
    setNewMessage('');
    scrollToBottom();
  };

  const filteredConversations = conversations.filter(conv =>
    conv.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b px-4 py-4">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          💬 Messages
        </h1>
      </div>

      <div className="flex-1 flex overflow-hidden">
        
        {/* Conversations Sidebar */}
        <div className="w-80 bg-white border-r flex flex-col">
          {/* Search */}
          <div className="p-4 border-b">
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" />
              <Input
                placeholder="Search conversations..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Conversation List */}
          <div className="flex-1 overflow-y-auto">
            {filteredConversations.map(conv => (
              <div
                key={conv.id}
                onClick={() => selectChat(conv)}
                className={`p-4 border-b cursor-pointer hover:bg-gray-50 transition-colors ${
                  activeChat?.id === conv.id ? 'bg-blue-50 border-l-4 border-l-blue-600' : ''
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className="relative">
                    <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-400 to-purple-600 flex items-center justify-center text-2xl">
                      {conv.avatar}
                    </div>
                    {conv.online && (
                      <div className="absolute bottom-0 right-0 h-3 w-3 bg-green-500 border-2 border-white rounded-full" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold truncate">{conv.name}</h3>
                      <span className="text-xs text-gray-500">{conv.time}</span>
                    </div>
                    <p className="text-sm text-gray-600 truncate">{conv.lastMessage}</p>
                  </div>
                  {conv.unread > 0 && (
                    <div className="h-5 w-5 bg-blue-600 rounded-full flex items-center justify-center">
                      <span className="text-xs text-white font-bold">{conv.unread}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col bg-gray-50">
          {activeChat ? (
            <>
              {/* Chat Header */}
              <div className="bg-white border-b px-6 py-4 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-600 flex items-center justify-center text-xl">
                    {activeChat.avatar}
                  </div>
                  <div>
                    <h2 className="font-semibold">{activeChat.name}</h2>
                    <p className="text-sm text-gray-500">
                      {activeChat.online ? '🟢 Active now' : 'Offline'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="icon">
                    <Phone className="h-5 w-5" />
                  </Button>
                  <Button variant="ghost" size="icon">
                    <Video className="h-5 w-5" />
                  </Button>
                  <Button variant="ghost" size="icon">
                    <MoreVertical className="h-5 w-5" />
                  </Button>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.map((msg, idx) => {
                  const isMe = msg.from_user_id === user.id;
                  const showAvatar = idx === 0 || messages[idx - 1].from_user_id !== msg.from_user_id;
                  
                  return (
                    <div
                      key={msg.id}
                      className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`flex items-end space-x-2 max-w-md ${isMe ? 'flex-row-reverse space-x-reverse' : ''}`}>
                        {showAvatar && !isMe && (
                          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-400 to-purple-600 flex items-center justify-center text-sm flex-shrink-0">
                            {activeChat.avatar}
                          </div>
                        )}
                        <div
                          className={`px-4 py-2 rounded-2xl ${
                            isMe
                              ? 'bg-blue-600 text-white rounded-br-sm'
                              : 'bg-white text-gray-800 rounded-bl-sm'
                          }`}
                        >
                          <p>{msg.content}</p>
                          <p className={`text-xs mt-1 ${isMe ? 'text-blue-100' : 'text-gray-500'}`}>
                            {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <div className="bg-white border-t px-6 py-4">
                <div className="flex items-center space-x-2">
                  <Button variant="ghost" size="icon">
                    <Paperclip className="h-5 w-5" />
                  </Button>
                  <Input
                    placeholder="Type a message..."
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    className="flex-1"
                  />
                  <Button onClick={sendMessage} disabled={!newMessage.trim()}>
                    <Send className="h-5 w-5" />
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center text-gray-500">
              <div className="text-center">
                <div className="text-6xl mb-4">💬</div>
                <h3 className="text-xl font-semibold mb-2">Select a conversation</h3>
                <p>Choose from your existing conversations or start a new one</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Messages;
