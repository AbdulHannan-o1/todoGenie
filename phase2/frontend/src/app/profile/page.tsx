"use client";

import { useState } from "react";
import { useAuth } from "@/context/auth-context";
import { useRouter } from "next/navigation";
import Sidebar from "../../components/layout/sidebar";
import { Menu, User, Mail, Calendar, Settings, Edit3, Shield, Key, Globe } from "lucide-react";

export default function ProfilePage() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800 text-white">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    router.push("/login");
    return null;
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
                <h1 className="text-2xl font-bold flex items-center">
                  <User className="mr-2 h-6 w-6 text-cyan-400" />
                  Profile
                </h1>
                <p className="text-slate-400 text-sm">Manage your account settings</p>
              </div>
            </div>
          </div>
        </header>

        {/* Profile Content */}
        <div className="p-6 max-w-4xl mx-auto">
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl overflow-hidden">
            <div className="p-6 border-b border-slate-700">
              <div className="flex items-center">
                <div className="bg-slate-700 rounded-full w-16 h-16 flex items-center justify-center mr-4">
                  <User className="h-8 w-8 text-cyan-400" />
                </div>
                <div>
                  <h2 className="text-xl font-bold">{user?.email?.split('@')[0] || 'User'}</h2>
                  <p className="text-slate-400">{user?.email}</p>
                </div>
              </div>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold flex items-center">
                    <User className="mr-2 h-5 w-5 text-cyan-400" />
                    Personal Information
                  </h3>
                  <div className="space-y-2">
                    <div className="flex items-center">
                      <Mail className="h-4 w-4 text-slate-400 mr-2" />
                      <span className="text-slate-300">{user?.email}</span>
                    </div>
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 text-slate-400 mr-2" />
                      <span className="text-slate-300">Joined: {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold flex items-center">
                    <Settings className="mr-2 h-5 w-5 text-cyan-400" />
                    Account Settings
                  </h3>
                  <div className="space-y-2">
                    <button className="w-full text-left p-2 rounded-lg bg-slate-700/50 hover:bg-slate-700 transition-colors flex items-center">
                      <Edit3 className="h-4 w-4 text-cyan-400 mr-2" />
                      Edit Profile
                    </button>
                    <button className="w-full text-left p-2 rounded-lg bg-slate-700/50 hover:bg-slate-700 transition-colors flex items-center">
                      <Shield className="h-4 w-4 text-cyan-400 mr-2" />
                      Security Settings
                    </button>
                    <button className="w-full text-left p-2 rounded-lg bg-slate-700/50 hover:bg-slate-700 transition-colors flex items-center">
                      <Key className="h-4 w-4 text-cyan-400 mr-2" />
                      Change Password
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}