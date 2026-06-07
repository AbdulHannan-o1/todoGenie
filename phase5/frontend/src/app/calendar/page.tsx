"use client";

import { useState } from "react";
import { useAuth } from "@/context/auth-context";
import { useRouter } from "next/navigation";
import Sidebar from "../../components/layout/sidebar";
import { Menu, Calendar as CalendarIcon, Plus } from "lucide-react";

export default function CalendarPage() {
  const { isAuthenticated, user, isLoading } = useAuth();
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
                  <CalendarIcon className="mr-2 h-6 w-6 text-cyan-400" />
                  Calendar
                </h1>
                <p className="text-slate-400 text-sm">Manage your schedule and deadlines</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <button
                className="flex items-center bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg transition-colors"
                onClick={() => router.push('/tasks/new')}
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Event
              </button>
            </div>
          </div>
        </header>

        {/* Calendar Content */}
        <div className="p-6">
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-8 text-center">
            <CalendarIcon className="h-16 w-16 text-cyan-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Calendar View</h2>
            <p className="text-slate-400 mb-6">Interactive calendar coming soon. This will show your tasks and deadlines.</p>
            <div className="grid grid-cols-7 gap-2 mb-6">
              {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => (
                <div key={day} className="text-slate-500 font-medium text-sm py-2">
                  {day}
                </div>
              ))}
              {/* Calendar days would go here in a real implementation */}
              {Array.from({ length: 35 }).map((_, index) => (
                <div key={index} className="border border-slate-700 rounded-lg p-2 h-20">
                  <div className="text-slate-400 text-xs">{index + 1}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}