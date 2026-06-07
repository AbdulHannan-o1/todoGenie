"use client";

import { useState } from "react";
import { useAuth } from "@/context/auth-context";
import { useRouter } from "next/navigation";
import Sidebar from "../../components/layout/sidebar";
import { Menu, Settings as SettingsIcon, Sun, Moon, Bell, Lock, Key, Globe, HelpCircle, LogOut } from "lucide-react";

export default function SettingsPage() {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
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

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

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
                  <SettingsIcon className="mr-2 h-6 w-6 text-cyan-400" />
                  Settings
                </h1>
                <p className="text-slate-400 text-sm">Configure your application preferences</p>
              </div>
            </div>
          </div>
        </header>

        {/* Settings Content */}
        <div className="p-6 max-w-4xl mx-auto">
          <div className="space-y-6">
            {/* Account Settings */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center">
                <SettingsIcon className="mr-2 h-5 w-5 text-cyan-400" />
                Account Settings
              </h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
                  <div className="flex items-center">
                    <Globe className="h-5 w-5 text-cyan-400 mr-3" />
                    <span>Language</span>
                  </div>
                  <select className="bg-slate-600 border border-slate-500 rounded px-3 py-1 text-sm">
                    <option>English</option>
                    <option>Spanish</option>
                    <option>French</option>
                  </select>
                </div>
                <div className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
                  <div className="flex items-center">
                    <Sun className="h-5 w-5 text-cyan-400 mr-3" />
                    <span>Theme</span>
                  </div>
                  <select className="bg-slate-600 border border-slate-500 rounded px-3 py-1 text-sm">
                    <option>System</option>
                    <option>Light</option>
                    <option>Dark</option>
                  </select>
                </div>
                <div className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg">
                  <div className="flex items-center">
                    <Bell className="h-5 w-5 text-cyan-400 mr-3" />
                    <span>Notifications</span>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input type="checkbox" className="sr-only peer" defaultChecked />
                    <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-600"></div>
                  </label>
                </div>
              </div>
            </div>

            {/* Security Settings */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center">
                <Lock className="mr-2 h-5 w-5 text-cyan-400" />
                Security Settings
              </h2>
              <div className="space-y-4">
                <button className="w-full text-left p-3 bg-slate-700/30 hover:bg-slate-700 rounded-lg flex items-center transition-colors">
                  <Key className="h-5 w-5 text-cyan-400 mr-3" />
                  <span>Change Password</span>
                </button>
                <button className="w-full text-left p-3 bg-slate-700/30 hover:bg-slate-700 rounded-lg flex items-center transition-colors">
                  <Lock className="h-5 w-5 text-cyan-400 mr-3" />
                  <span>Two-Factor Authentication</span>
                </button>
              </div>
            </div>

            {/* Support & Help */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center">
                <HelpCircle className="mr-2 h-5 w-5 text-cyan-400" />
                Support & Help
              </h2>
              <div className="space-y-4">
                <button className="w-full text-left p-3 bg-slate-700/30 hover:bg-slate-700 rounded-lg flex items-center transition-colors">
                  <HelpCircle className="h-5 w-5 text-cyan-400 mr-3" />
                  <span>Help Center</span>
                </button>
                <button className="w-full text-left p-3 bg-slate-700/30 hover:bg-slate-700 rounded-lg flex items-center transition-colors">
                  <SettingsIcon className="h-5 w-5 text-cyan-400 mr-3" />
                  <span>Documentation</span>
                </button>
              </div>
            </div>

            {/* Danger Zone */}
            <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6">
              <h2 className="text-xl font-bold mb-4 text-red-400 flex items-center">
                <LogOut className="mr-2 h-5 w-5" />
                Danger Zone
              </h2>
              <button
                onClick={handleLogout}
                className="w-full text-left p-3 bg-red-900/30 hover:bg-red-900/50 rounded-lg flex items-center transition-colors text-red-400"
              >
                <LogOut className="h-5 w-5 mr-3" />
                <span>Sign Out</span>
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}