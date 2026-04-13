"use client";

import { useEffect, useRef, useState } from "react";
import { useAuth } from "@/context/auth-context";
import { useRouter } from "next/navigation";
import Sidebar from "../../components/layout/sidebar";
import { Menu, Send, Bot, User, Sparkles } from "lucide-react";

interface Message {
  id: number | string;
  text: string;
  sender: 'user' | 'bot';
}

interface ChatKitMessage {
  id: string;
  senderId: string;
  text: string;
  createdAt: string;
}

export default function ChatKitChat() {
  const { isAuthenticated, isLoading: authIsLoading, token } = useAuth();
  const router = useRouter();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isConversationsSidebarOpen, setIsConversationsSidebarOpen] = useState(false);

  // ChatKit state
  const [chatkit, setChatkit] = useState<any>(null);
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showConfig, setShowConfig] = useState(false);

  const messagesEndRef = useRef<null | HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Load ChatKit SDK once
  useEffect(() => {
    const loadChatKitSDK = async () => {
      if (typeof window !== 'undefined' && !(window as any).Chatkit) {
        try {
          // Use UMD build from CDN
          const response = await fetch('https://cdn.jsdelivr.net/npm/@openai/chatkit@latest/dist/chatkit.umd.min.js');
          if (!response.ok) {
            throw new Error('Failed to load ChatKit SDK');
          }
        } catch (error) {
          console.error('Failed to load ChatKit SDK:', error);
        }
      }
    };
    loadChatKitSDK();
  }, []);

  // Initialize from stored conversation state if available
  useEffect(() => {
    const initializeFromStorage = async () => {
      if (typeof window !== 'undefined') {
        try {
          const { loadConversationState } = await import('@/utils/conversation-storage');
          const state = loadConversationState();
          if (state && state.messages.length > 0) {
            setMessages(state.messages);
            if (state.selectedConversationId) {
              // Load conversation from backend if selected
              await loadConversationHistory(state.selectedConversationId);
            }
          }
        } catch (error) {
          console.error('Error loading conversation from storage:', error);
        }
      }
    };

    initializeFromStorage();
  }, []);

  // Load conversation history from backend
  const loadConversationHistory = async (conversationId: string) => {
    try {
      const response = await fetch(`/api/v1/chat/conversations/${conversationId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });
      if (response.ok) {
        const data = await response.json();
        const formattedMessages = data.messages.map((msg: any, index: number) => ({
          id: msg.id || (index + 1),
          text: msg.content,
          sender: msg.role === 'assistant' ? 'bot' : 'user',
        }));
        setMessages(formattedMessages);
      }
    } catch (error) {
      console.error('Error loading conversation history:', error);
    }
  };

  // Initialize ChatKit
  useEffect(() => {
    const initChatKit = async () => {
      try {
        // Load configuration from localStorage
        const openaiApiKey = localStorage.getItem('openai_api_key');
        const chatkitLocator = localStorage.getItem('chatkit_locator_key');
        const chatkitSecret = localStorage.getItem('chatkit_secret_key');

        if (!openaiApiKey || !chatkitLocator || !chatkitSecret) {
          setShowConfig(true);
          return;
        }

        // Check if ChatKit SDK is loaded
        if (!(window as any).Chatkit) {
          setError('ChatKit SDK not loaded. Please refresh the page.');
          return;
        }

        // Create Chatkit instance using global variable
        const Chatkit = (window as any).Chatkit;
        const chatkitInstance = new Chatkit.default({
          instanceLocatorKey: chatkitLocator,
          key: chatkitSecret,
          defaultGlobalRoom: 'todo-ai-tasks',
          debug: true
        });

        setChatkit(chatkitInstance);
      } catch (error) {
        console.error('Failed to initialize ChatKit:', error);
        setError('Failed to load ChatKit SDK. Please refresh the page.');
      }
    };

    initChatKit();
  }, []);

  // Connect to ChatKit
  useEffect(() => {
    if (chatkit) {
      chatkit.connect({
        onConnected: () => {
          console.log('Connected to ChatKit');
          setConnected(true);
          setShowConfig(false);

          // Join the default room
          chatkit.joinRoom({
            roomId: 'todo-ai-tasks'
          })
            .catch((err: any) => {
              console.error('Failed to join room:', err);
            });
        },
        onDisconnected: () => {
          console.log('Disconnected from ChatKit');
          setConnected(false);
        },
        onError: (error: any) => {
          console.error('ChatKit error:', error);
          setError('Failed to connect to ChatKit. Please check your configuration.');
        }
      });
    }
  }, [chatkit]);

  // Handle ChatKit messages
  useEffect(() => {
    if (chatkit) {
      const handleMessage = (message: ChatKitMessage) => {
        console.log('Received message:', message);
        const formattedMessage: Message = {
          id: message.id,
          text: message.text,
          sender: message.senderId === 'user' ? 'user' : 'bot',
        };
        setMessages(prev => [...prev, formattedMessage]);
      };

      chatkit.on('message', handleMessage);

      return () => {
        chatkit.off('message', handleMessage);
      };
    }
  }, [chatkit]);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !chatkit || !connected) return;

    setIsLoading(true);

    // Add user message to display
    const userMessage: Message = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user',
    };
    setMessages(prev => [...prev, userMessage]);

    // Send to backend API for AI processing
    try {
      const requestBody = {
        content: inputMessage,
        message_type: 'text',
      };

      const response = await fetch(`/api/v1/chat/send`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Add AI response
      const botMessage: Message = {
        id: Date.now() + 1,
        text: data.response || "I processed your request successfully.",
        sender: 'bot',
      };
      setMessages(prev => [...prev, botMessage]);

      // Save conversation state to localStorage
      const { saveConversationState } = await import('@/utils/conversation-storage');
      saveConversationState({
        conversationId: data.conversation_id || null,
        messages: [...messages, userMessage, botMessage],
        selectedConversationId: data.conversation_id || null,
      });
    } catch (error: any) {
      console.error('Error sending message:', error);
      setError(error.message || 'Sorry, I encountered an error processing your request. Please try again.');

      const errorMessage: Message = {
        id: Date.now() + 1,
        text: error.message || "Sorry, I encountered an error processing your request. Please try again.",
        sender: 'bot',
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setInputMessage("");
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (authIsLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800 text-white">
        Loading...
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800 text-white">
        Loading or redirecting...
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white">
      <Sidebar isCollapsed={isSidebarCollapsed} toggleSidebar={() => setIsSidebarCollapsed(!isSidebarCollapsed)} />

      <main className={`flex-1 transition-all duration-300 ${isSidebarCollapsed ? 'md:ml-16' : 'md:ml-64'}`}>
        {/* Navbar */}
        <header className="sticky top-0 z-10 bg-slate-800/80 backdrop-blur-sm border-b border-slate-700">
          <div className="flex items-center justify-between p-4">
            <div className="flex items-center">
              <button
                onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
                className="mr-4 p-2 rounded-lg bg-slate-700/50 hover:bg-slate-700 transition-colors"
              >
                <Menu className="h-5 w-5 text-slate-300" />
              </button>
              <div>
                <h1 className="text-2xl font-bold">AI Chat Assistant</h1>
                <p className="text-slate-400 text-sm">ChatKit powered • {connected ? '✓ Connected' : '✗ Disconnected'}</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={() => setIsConversationsSidebarOpen(!isConversationsSidebarOpen)}
                className="p-2 rounded-lg bg-slate-700/50 hover:bg-slate-700 transition-colors"
              >
                <Menu className="h-5 w-5 text-slate-300" />
              </button>

              {showConfig && (
                <button
                  onClick={() => setShowConfig(true)}
                  className="p-2 rounded-lg bg-cyan-600/50 hover:bg-cyan-600 transition-colors"
                  title="Configure ChatKit"
                >
                  <Sparkles className="h-5 w-5 text-white" />
                </button>
              )}

              <div className="w-8 h-8 rounded-full bg-cyan-600 flex items-center justify-center">
                <Sparkles className="h-4 w-4" />
              </div>
            </div>
          </div>
        </header>

        {/* Chat Container */}
        <div className="flex flex-col h-[calc(100vh-73px)]">
          {showConfig && <ChatKitConfig onClose={() => setShowConfig(false)} />}

          {error && (
            <div className="bg-red-500/20 border border-red-500 text-red-200 p-3 m-4 rounded-lg">
              <div className="flex justify-between items-center">
                <span>{error}</span>
                <button
                  onClick={() => setError(null)}
                  className="text-red-300 hover:text-white"
                >
                  ×
                </button>
              </div>
            </div>
          )}

          {!showConfig && (
            <>
              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={messagesContainerRef}>
                {messages.length === 0 ? (
                  <div className="flex items-center justify-center h-full text-slate-400">
                    <div className="text-center">
                      <Bot className="h-12 w-12 mx-auto mb-4 text-cyan-400" />
                      <p>Hello! I'm your AI assistant. How can I help you with your tasks today?</p>
                    </div>
                  </div>
                ) : (
                  messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                          message.sender === "user"
                            ? "bg-cyan-600 rounded-br-none"
                            : "bg-slate-800 border border-slate-700 rounded-bl-none"
                        }`}
                      >
                        <div className="flex items-start space-x-2">
                          {message.sender === "bot" && (
                            <div className="flex-shrink-0 pt-0.5">
                              <Bot className="h-5 w-5 text-cyan-400" />
                            </div>
                          )}
                          <p className="text-white whitespace-pre-wrap">{message.text}</p>
                          {message.sender === "user" && (
                            <div className="flex-shrink-0 pt-0.5">
                              <User className="h-5 w-5 text-white" />
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))
                )}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="max-w-[80%] bg-slate-800 border border-slate-700 rounded-2xl rounded-bl-none px-4 py-3">
                      <div className="flex items-center space-x-2">
                        <Bot className="h-5 w-5 text-cyan-400" />
                        <div className="flex space-x-1">
                          <div className="h-2 w-2 bg-slate-400 rounded-full animate-bounce"></div>
                          <div className="h-2 w-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                          <div className="h-2 w-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="border-t border-slate-700 p-4">
                <div className="flex items-end space-x-2">
                  <div className="flex-1 relative">
                    <textarea
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Type a message... (e.g., 'Add a task to buy groceries tomorrow')"
                      className="w-full bg-slate-800 border border-slate-700 rounded-lg py-3 px-4 text-white placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 resize-none"
                      rows={2}
                      disabled={!connected}
                    />
                  </div>
                  <button
                    onClick={handleSendMessage}
                    disabled={!connected || isLoading || !inputMessage.trim()}
                    className="h-12 w-12 flex items-center justify-center bg-cyan-600 hover:bg-cyan-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Send className="h-5 w-5" />
                  </button>
                </div>

                {/* Suggestions */}
                <div className="mt-3 flex flex-wrap gap-2">
                  {[
                    "Add a task to buy groceries tomorrow",
                    "Show me pending tasks",
                    "Mark task 3 as complete",
                    "Reschedule my meeting to 2 PM"
                  ].map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => setInputMessage(suggestion)}
                      className="text-xs bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-full px-3 py-1.5 transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>

        {/* Conversations sidebar */}
        <div className={`fixed top-0 right-0 h-full bg-slate-800 border-l border-slate-700 z-50 transform transition-transform duration-300 ease-in-out ${
          isConversationsSidebarOpen ? 'translate-x-0 w-64 md:w-80' : 'translate-x-full w-64 md:w-80'
        }`}>
          <div className="p-4 border-b border-slate-700 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Conversations</h2>
            <button
              onClick={() => setIsConversationsSidebarOpen(false)}
              className="p-1 rounded-lg bg-slate-700 hover:bg-slate-600 transition-colors"
            >
              <span className="text-lg">×</span>
            </button>
          </div>

          <div className="p-4 border-b border-slate-700">
            <button
              onClick={async () => {
                setMessages([]);
                const { clearConversationState } = await import('@/utils/conversation-storage');
                clearConversationState();
              }}
              className="w-full py-2 rounded-lg bg-cyan-600 hover:bg-cyan-700 transition-colors font-medium"
            >
              + New Chat
            </button>
          </div>

          <div className="overflow-y-auto h-[calc(100vh-145px)]">
            <div className="p-4 text-center text-slate-400">
              Conversations sync from backend
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

// ChatKit Configuration Component
function ChatKitConfig({ onClose }: { onClose: () => void }) {
  const [openaiKey, setOpenaiKey] = useState("");
  const [locatorKey, setLocatorKey] = useState("");
  const [secretKey, setSecretKey] = useState("");
  const [status, setStatus] = useState<{ type: 'success' | 'error', message: string } | null>(null);

  useEffect(() => {
    // Load saved config
    setOpenaiKey(localStorage.getItem('openai_api_key') || '');
    setLocatorKey(localStorage.getItem('chatkit_locator_key') || '');
    setSecretKey(localStorage.getItem('chatkit_secret_key') || '');
  }, []);

  const handleSave = () => {
    if (!openaiKey || !locatorKey || !secretKey) {
      setStatus({ type: 'error', message: 'Please fill in all fields' });
      return;
    }

    localStorage.setItem('openai_api_key', openaiKey);
    localStorage.setItem('chatkit_locator_key', locatorKey);
    localStorage.setItem('chatkit_secret_key', secretKey);

    setStatus({ type: 'success', message: 'Configuration saved!' });
    setTimeout(onClose, 1500);
  };

  return (
    <div className="flex items-center justify-center h-full p-4">
      <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 max-w-md w-full">
        <h2 className="text-xl font-bold mb-4">Configure ChatKit</h2>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">OpenAI API Key</label>
            <input
              type="password"
              value={openaiKey}
              onChange={(e) => setOpenaiKey(e.target.value)}
              placeholder="sk-..."
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white placeholder:text-slate-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">ChatKit Instance Locator Key</label>
            <input
              type="text"
              value={locatorKey}
              onChange={(e) => setLocatorKey(e.target.value)}
              placeholder="v1:YOUR-INSTANCE-LOCATOR-KEY"
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white placeholder:text-slate-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">ChatKit Secret Key</label>
            <input
              type="password"
              value={secretKey}
              onChange={(e) => setSecretKey(e.target.value)}
              placeholder="your-chatkit-secret-key"
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-white placeholder:text-slate-500"
            />
          </div>

          {status && (
            <div className={`p-3 rounded-lg ${status.type === 'success' ? 'bg-green-500/20 text-green-200' : 'bg-red-500/20 text-red-200'}`}>
              {status.message}
            </div>
          )}

          <button
            onClick={handleSave}
            className="w-full py-2 bg-cyan-600 hover:bg-cyan-700 rounded-lg font-medium"
          >
            Save Configuration
          </button>

          <div className="text-xs text-slate-400 mt-2">
            <p className="font-medium mb-1">How to get ChatKit credentials:</p>
            <ol className="list-decimal list-inside space-y-1">
              <li>Go to <a href="https://platform.openai.com/settings/organization/security/domain-allowlist" target="_blank" className="text-cyan-400 underline">OpenAI Dashboard</a></li>
              <li>Add your domain (or use localhost for testing)</li>
              <li>Create a ChatKit instance and get your keys</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}

// Sidebar component (defined separately to avoid duplicate)
