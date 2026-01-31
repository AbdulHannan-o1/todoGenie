"use client";

import { useState, useEffect, useRef } from "react";
import { useAuth } from "@/context/auth-context";
import { useRouter } from "next/navigation";
import Sidebar from "../../components/layout/sidebar";
import VoiceInput from "../../components/Chat/VoiceInput";
import { Menu, Send, Bot, User, Sparkles } from "lucide-react";

export default function ChatPage() {
  const { isAuthenticated, isLoading: authIsLoading, token } = useAuth();
  const router = useRouter();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isConversationsSidebarOpen, setIsConversationsSidebarOpen] = useState(false);
  // Define types for better TypeScript support
  type Message = {
    id: number | string;
    text: string;
    sender: 'user' | 'bot';
  };

  type Conversation = {
    id: string;
    title: string;
    created_at: string;
    updated_at: string;
    message_count: number;
  };

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isConversationsLoading, setIsConversationsLoading] = useState(true); // Start as loading
  const [error, setError] = useState<string | null>(null);

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
              setSelectedConversationId(state.selectedConversationId);
            }
          }
        } catch (error) {
          console.error('Error loading conversation from storage:', error);
        }
      }
    };

    initializeFromStorage();
  }, []);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  useEffect(() => {
    if (authIsLoading) {
      // Still loading auth state, don't redirect yet
      return;
    }
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, authIsLoading, router]);

  useEffect(() => {
    if (isAuthenticated && !authIsLoading) {
      // Check if there's an active conversation in storage before loading all conversations
      const checkAndLoadConversation = async () => {
        try {
          const { hasActiveConversation, loadConversationState } = await import('@/utils/conversation-storage');

          if (hasActiveConversation()) {
            // If there's an active conversation in storage, use it
            const storedState = loadConversationState();
            if (storedState) {
              setMessages(storedState.messages);
              if (storedState.selectedConversationId) {
                setSelectedConversationId(storedState.selectedConversationId);
              }
            }
          } else {
            // Otherwise, load conversations and initialize with welcome message
            loadConversationsWithWelcome();
          }
        } catch (error) {
          console.error('Error checking stored conversation:', error);
          // Fallback to loading conversations normally
          loadConversationsWithWelcome();
        }
      };

      checkAndLoadConversation();
    }
  }, [isAuthenticated, authIsLoading]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Clear conversation state when user logs out
  useEffect(() => {
    if (!isAuthenticated && !authIsLoading) {
      const clearStoredConversation = async () => {
        try {
          const { clearConversationState } = await import('@/utils/conversation-storage');
          clearConversationState();
        } catch (error) {
          console.error('Error clearing conversation state on logout:', error);
        }
      };

      clearStoredConversation();
    }
  }, [isAuthenticated, authIsLoading]);

  // Removed the useEffect that loads conversation history based on selectedConversationId
  // It's now handled in loadConversationsAndLatest

  const loadConversationsWithWelcome = async () => {
    setIsConversationsLoading(true);
    try {
      // Fetch all conversations from API (ignore any cached conversation for auto-selection)
      const response = await fetch('/api/v1/chat/conversations', {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });
      if (response.ok) {
        const data = await response.json();
        setConversations(data);

        // Never auto-select any conversation, always show welcome message
        setSelectedConversationId(null);
        setMessages([
          { id: 1, text: "Hello! I'm your AI assistant. How can I help you with your tasks today?", sender: "bot" },
        ]);
      } else {
        // If API fails, show welcome message
        setMessages([
          { id: 1, text: "Hello! I'm your AI assistant. How can I help you with your tasks today?", sender: "bot" },
        ]);
        setSelectedConversationId(null);
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
      // In case of error, show welcome message
      setMessages([
        { id: 1, text: "Hello! I'm your AI assistant. How can I help you with your tasks today?", sender: "bot" },
      ]);
      setSelectedConversationId(null);
    } finally {
      setIsConversationsLoading(false);
    }
  };

  const loadConversationsAndLatest = async () => {
    setIsConversationsLoading(true);
    try {
      // First check if we have a cached conversation
      const cachedConversation = await import('@/utils/conversation-preloader').then(mod => mod.getRecentConversationFromCache());

      if (cachedConversation) {
        // Use cached data if available
        const { conversation, history } = cachedConversation;
        setConversations([conversation]); // Set as if this is the only conversation for now
        setSelectedConversationId(conversation.id);

        // Transform backend messages to frontend format
        const formattedMessages = history.messages.map((msg: any, index: number) => ({
          id: msg.id || (index + 1),
          text: msg.content,
          sender: msg.role === 'assistant' ? 'bot' : 'user',
        }));
        setMessages(formattedMessages);
      } else {
        // If no cache, fetch from API as before
        const response = await fetch('/api/v1/chat/conversations', {
          headers: {
            'Authorization': `Bearer ${token}`,
          }
        });
        if (response.ok) {
          const data = await response.json();
          setConversations(data);

          if (data.length > 0) {
            // Don't auto-select the most recent conversation automatically anymore
            // The user will select a conversation manually
            setSelectedConversationId(null);
            setMessages([
              { id: 1, text: "Hello! I'm your AI assistant. How can I help you with your tasks today?", sender: "bot" },
            ]);
          } else {
            // If no conversations exist, show welcome message
            setMessages([
              { id: 1, text: "Hello! I'm your AI assistant. How can I help you with your tasks today?", sender: "bot" },
            ]);
            setSelectedConversationId(null);
          }
        }
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
      // In case of error, show welcome message
      setMessages([
        { id: 1, text: "Hello! I'm your AI assistant. How can I help you with your tasks today?", sender: "bot" },
      ]);
      setSelectedConversationId(null);
    } finally {
      setIsConversationsLoading(false);
    }
  };

  const loadConversations = async () => {
    // Existing function to refresh conversation list without changing current view
    try {
      const response = await fetch('/api/v1/chat/conversations', {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });
      if (response.ok) {
        const data = await response.json();
        setConversations(data);
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
    }
  };

  const loadConversationHistory = async (conversationId: string) => {
    try {
      const response = await fetch(`/api/v1/chat/conversations/${conversationId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });
      if (response.ok) {
        const data = await response.json();
        // Transform backend messages to frontend format
        const formattedMessages = data.messages.map((msg: any, index: number) => ({
          id: msg.id || (index + 1),
          text: msg.content,
          sender: msg.role === 'assistant' ? 'bot' : 'user',
        }));
        setMessages(formattedMessages);
      } else {
        // If conversation doesn't exist yet, start with empty messages
        setMessages([]);
      }
    } catch (error) {
      console.error('Error loading conversation history:', error);
      setMessages([
        { id: 1, text: "Hello! I'm your AI assistant. How can I help you with your tasks today?", sender: "bot" },
      ]);
    }
  };

  const createNewConversation = async () => {
    setSelectedConversationId(null);

    // Clear conversation state from localStorage
    const { clearConversationState } = await import('@/utils/conversation-storage');
    clearConversationState();

    setMessages([
      { id: 1, text: "Hello! I'm your AI assistant. How can I help you with your tasks today?", sender: "bot" },
    ]);
    // Reload conversations to update the list
    loadConversations();
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    // Add user message
    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: "user" as const,
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInputMessage("");
    setIsLoading(true);

    try {
      // Send message to backend API
      const params = new URLSearchParams({
        content: inputMessage,
        message_type: 'text', // or 'voice' if coming from voice input
      });
      if (selectedConversationId) {
        params.append('conversation_id', selectedConversationId);
      }

      const response = await fetch(`/api/v1/chat/send?${params}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Update the selected conversation ID if it was created
      let newSelectedConversationId = selectedConversationId;
      if (data.conversation_id && !selectedConversationId) {
        newSelectedConversationId = data.conversation_id;
        setSelectedConversationId(newSelectedConversationId);
        // Refresh the conversation list
        loadConversations();
      }

      // Add AI response
      const botResponse = {
        id: Date.now() + 1,
        text: data.response || "I processed your request successfully.",
        sender: "bot" as const,
      };

      const finalMessages = [...updatedMessages, botResponse];
      setMessages(finalMessages);

      // Save conversation state to localStorage
      const { saveConversationState } = await import('@/utils/conversation-storage');
      saveConversationState({
        conversationId: data.conversation_id || newSelectedConversationId,
        messages: finalMessages,
        selectedConversationId: newSelectedConversationId,
      });
    } catch (error: any) {
      console.error('Error sending message:', error);

      // Set error state
      setError(error.message || 'Sorry, I encountered an error processing your request. Please try again.');

      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        text: error.message || "Sorry, I encountered an error processing your request. Please try again.",
        sender: "bot" as const,
      };

      const finalMessages = [...updatedMessages, errorMessage];
      setMessages(finalMessages);

      // Save conversation state to localStorage including error
      const { saveConversationState } = await import('@/utils/conversation-storage');
      saveConversationState({
        conversationId: selectedConversationId,
        messages: finalMessages,
        selectedConversationId: selectedConversationId,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const decodeHTMLEntities = (text: string): string => {
    return text
      .replace(/&#x27;/g, "'")      // Single quote
      .replace(/&quot;/g, '"')       // Double quote
      .replace(/&lt;/g, '<')         // Less than
      .replace(/&gt;/g, '>')         // Greater than
      .replace(/&amp;/g, '&')        // Ampersand
      .replace(/&#(\d+);/g, (_, numStr) => String.fromCharCode(parseInt(numStr, 10))) // Numeric entities
      .replace(/&([a-z]+);/gi, (_, entity) => {
        // Basic named entities map
        const entities: {[key: string]: string} = {
          'amp': '&',
          'lt': '<',
          'gt': '>',
          'quot': '"',
          'apos': "'",
          'nbsp': ' '
        };
        return entities[entity.toLowerCase()] || `&${entity};`;
      });
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
                <p className="text-slate-400 text-sm">Ask me anything about your tasks</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Toggle button for conversations sidebar */}
              <button
                onClick={() => setIsConversationsSidebarOpen(!isConversationsSidebarOpen)}
                className="p-2 rounded-lg bg-slate-700/50 hover:bg-slate-700 transition-colors"
              >
                <Menu className="h-5 w-5 text-slate-300" />
              </button>

              {selectedConversationId && (
                <button
                  onClick={async () => {
                    if (confirm('Are you sure you want to delete this conversation?')) {
                      try {
                        const response = await fetch(`/api/v1/chat/conversations/${selectedConversationId}`, {
                          method: 'DELETE',
                          headers: {
                            'Authorization': `Bearer ${token}`,
                          },
                        });

                        if (response.ok) {
                          // Remove the deleted conversation from the local list
                          setConversations(prev => prev.filter(conv => conv.id !== selectedConversationId));

                          // If this was the selected conversation, clear selection and show welcome message
                          if (selectedConversationId) {
                            setSelectedConversationId(null);

                            // Clear conversation state from localStorage
                            const { clearConversationState } = await import('@/utils/conversation-storage');
                            clearConversationState();

                            setMessages([
                              { id: 1, text: "Hello! I'm your AI assistant. How can I help you with your tasks today?", sender: "bot" },
                            ]);
                          }

                          // Reload conversations list
                          loadConversations();
                        } else {
                          console.error('Error deleting conversation:', response.statusText);
                        }
                      } catch (error) {
                        console.error('Error deleting conversation:', error);
                      }
                    }
                  }}
                  className="p-2 rounded-lg bg-red-600/50 hover:bg-red-600 transition-colors"
                >
                  Delete
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
          {/* Error display */}
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

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
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
                    <p className="text-white whitespace-pre-wrap">{decodeHTMLEntities(message.text)}</p>
                    {message.sender === "user" && (
                      <div className="flex-shrink-0 pt-0.5">
                        <User className="h-5 w-5 text-white" />
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
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
                />
              </div>
              <div className="flex flex-col space-y-2">
                <button
                  onClick={handleSendMessage}
                  disabled={isLoading || !inputMessage.trim()}
                  className="h-12 w-12 flex items-center justify-center bg-cyan-600 hover:bg-cyan-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="h-5 w-5" />
                </button>
                <VoiceInput
                  onTranscript={(transcript) => {
                    // Set the transcribed text to the input field
                    setInputMessage(transcript);
                    // Automatically send the message after transcription
                    if (transcript.trim()) {
                      // Update the message type to voice in the fetch call
                      const handleVoiceSendMessage = async () => {
                        // Add user message
                        const userMessage = {
                          id: Date.now(),
                          text: transcript,
                          sender: "user" as const,
                        };

                        const updatedMessages = [...messages, userMessage];
                        setMessages(updatedMessages);
                        setIsLoading(true);

                        try {
                          // Send message to backend API with voice type
                          const params = new URLSearchParams({
                            content: transcript,
                            message_type: 'voice',
                          });
                          if (selectedConversationId) {
                            params.append('conversation_id', selectedConversationId);
                          }

                          const response = await fetch(`/api/v1/chat/send?${params}`, {
                            method: 'POST',
                            headers: {
                              'Authorization': `Bearer ${token}`,
                            },
                          });

                          if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                          }

                          const data = await response.json();

                          // Update the selected conversation ID if it was created
                          let newSelectedConversationId = selectedConversationId;
                          if (data.conversation_id && !selectedConversationId) {
                            newSelectedConversationId = data.conversation_id;
                            setSelectedConversationId(newSelectedConversationId);
                            // Refresh the conversation list
                            loadConversations();
                          }

                          // Add AI response
                          const botResponse = {
                            id: Date.now() + 1,
                            text: data.response || "I processed your voice request successfully.",
                            sender: "bot" as const,
                          };

                          const finalMessages = [...updatedMessages, botResponse];
                          setMessages(finalMessages);

                          // Save conversation state to localStorage
                          const { saveConversationState } = await import('@/utils/conversation-storage');
                          saveConversationState({
                            conversationId: data.conversation_id || newSelectedConversationId,
                            messages: finalMessages,
                            selectedConversationId: newSelectedConversationId,
                          });
                        } catch (error: any) {
                          console.error('Error sending voice message:', error);

                          // Set error state
                          setError(error.message || 'Sorry, I encountered an error processing your voice request. Please try again.');

                          // Add error message
                          const errorMessage = {
                            id: Date.now() + 1,
                            text: error.message || "Sorry, I encountered an error processing your voice request. Please try again.",
                            sender: "bot" as const,
                          };

                          const finalMessages = [...updatedMessages, errorMessage];
                          setMessages(finalMessages);

                          // Save conversation state to localStorage including error
                          const { saveConversationState } = await import('@/utils/conversation-storage');
                          saveConversationState({
                            conversationId: selectedConversationId,
                            messages: finalMessages,
                            selectedConversationId: selectedConversationId,
                          });
                        } finally {
                          setIsLoading(false);
                        }
                      };

                      handleVoiceSendMessage();
                    }
                  }}
                  disabled={isLoading}
                />
              </div>
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
        </div>

        {/* Conversations sidebar - appears on the right when toggled */}
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
              onClick={() => {
                createNewConversation();
                setIsConversationsSidebarOpen(false); // Close sidebar after creating new conversation
              }}
              className="w-full py-2 rounded-lg bg-cyan-600 hover:bg-cyan-700 transition-colors font-medium"
            >
              + New Chat
            </button>
          </div>

          <div className="overflow-y-auto h-[calc(100vh-145px)]">
            {isConversationsLoading ? (
              <div className="p-4 text-center text-slate-400">Loading conversations...</div>
            ) : conversations.length === 0 ? (
              <div className="p-4 text-center text-slate-400">No conversations yet</div>
            ) : (
              <div className="p-2">
                {conversations.map((conversation) => (
                  <div
                    key={conversation.id}
                    className={`p-3 rounded-lg mb-2 cursor-pointer transition-colors ${
                      selectedConversationId === conversation.id
                        ? 'bg-cyan-600/20 border border-cyan-500'
                        : 'bg-slate-700/50 hover:bg-slate-700'
                    }`}
                    onClick={async () => {
                      setSelectedConversationId(conversation.id);

                      // Load conversation history from backend
                      try {
                        const response = await fetch(`/api/v1/chat/conversations/${conversation.id}`, {
                          headers: {
                            'Authorization': `Bearer ${token}`,
                          }
                        });

                        if (response.ok) {
                          const data = await response.json();
                          // Transform backend messages to frontend format
                          const formattedMessages = data.messages.map((msg: any, index: number) => ({
                            id: msg.id || (index + 1),
                            text: msg.content,
                            sender: msg.role === 'assistant' ? 'bot' : 'user',
                          }));

                          setMessages(formattedMessages);

                          // Save conversation state to localStorage
                          const { saveConversationState } = await import('@/utils/conversation-storage');
                          saveConversationState({
                            conversationId: conversation.id,
                            messages: formattedMessages,
                            selectedConversationId: conversation.id,
                          });
                        } else {
                          // If conversation doesn't exist yet, start with empty messages
                          setMessages([]);
                        }
                      } catch (error) {
                        console.error('Error loading conversation history:', error);
                        setMessages([
                          { id: 1, text: "Hello! I'm your AI assistant. How can I help you with your tasks today?", sender: "bot" },
                        ]);
                      }

                      setIsConversationsSidebarOpen(false); // Close sidebar after selection
                    }}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium truncate">
                          {conversation.title || `Conversation ${conversation.id.substring(0, 8)}`}
                        </h3>
                        <p className="text-xs text-slate-400 mt-1">
                          {conversation.message_count} {conversation.message_count === 1 ? 'message' : 'messages'}
                        </p>
                      </div>
                      <span className="text-xs text-slate-500 whitespace-nowrap">
                        {new Date(conversation.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}