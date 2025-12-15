"use client";

import { useState, useEffect, useRef } from "react";
import { useAuth } from "@/context/auth-context";
import { useRouter } from "next/navigation";
import Sidebar from "../../components/layout/sidebar";
import { Send, Bot, User, Sparkles } from "lucide-react";

export default function ChatPage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! I'm your AI assistant. How can I help you with your tasks today?", sender: "bot" },
  ]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const botResponse = {
        id: Date.now() + 1,
        text: "I received your message: '" + inputMessage + "'. In a real implementation, I would process this with natural language and interact with the task management system.",
        sender: "bot" as const,
      };

      setMessages((prev) => [...prev, botResponse]);
      setIsLoading(false);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

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
              <Sparkles className="h-6 w-6 text-cyan-400 mr-2" />
              <h1 className="text-2xl font-bold">AI Chat Assistant</h1>
            </div>
          </div>
        </header>

        {/* Chat Container */}
        <div className="flex flex-col h-[calc(100vh-73px)]">
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
                    <p className="text-white">{message.text}</p>
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
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !inputMessage.trim()}
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
        </div>
      </main>
    </div>
  );
}