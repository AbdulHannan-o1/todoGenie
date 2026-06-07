'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, ListTodo, Calendar, Settings, User, MessageCircle, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '@/context/auth-context';
import { toast } from 'sonner';

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Tasks', href: '/tasks', icon: ListTodo },
  { name: 'Calendar', href: '/calendar', icon: Calendar },
  { name: 'AI Chat', href: '/chat', icon: MessageCircle },
  { name: 'Profile', href: '/profile', icon: User },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Sidebar({ isCollapsed, toggleSidebar }: { isCollapsed: boolean; toggleSidebar: () => void }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);

  const handleLogout = () => {
    logout();
    toast.info('You have been logged out.');
    window.location.href = '/login';
  };

  // For mobile responsiveness
  const toggleMobileMenu = () => setIsOpen(!isOpen);

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={toggleMobileMenu}
        className="md:hidden absolute top-4 left-4 p-2 rounded-md text-slate-400 hover:text-white hover:bg-slate-800"
      >
        {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </button>

      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-screen bg-slate-900 border-r border-slate-700 z-30 transition-all duration-300 ${
          isOpen ? 'w-64' : 'w-0'
        } ${isCollapsed ? 'md:w-16' : 'md:w-64'}`}
      >
        <div className={`h-full flex flex-col ${isOpen ? 'block' : 'hidden md:block'}`}>
          {/* Logo */}
          <div className={`flex items-center border-b border-slate-700 p-4 ${isCollapsed ? 'justify-center' : 'justify-between'}`}>
            {!isCollapsed && (
              <div className="flex items-center space-x-2">
                <div className="bg-cyan-600 w-8 h-8 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">T</span>
                </div>
                <span className="text-white font-semibold text-xl">TodoGenie</span>
              </div>
            )}
            {isCollapsed && (
              <div className="bg-cyan-600 w-8 h-8 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">T</span>
              </div>
            )}
            <button
              onClick={toggleSidebar}
              className="md:hidden ml-auto p-1 rounded-md text-slate-400 hover:text-white"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Main Content with User Info at Bottom */}
          <div className="flex-1 flex flex-col h-full">
            {/* Navigation container with overflow */}
            <div className="flex-1 overflow-y-auto">
              <nav className="py-2">
                <ul className="space-y-1 px-2">
                  {navItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname === item.href;
                    return (
                      <li key={item.href}>
                        <Link
                          href={item.href}
                          className={`flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                            isActive
                              ? 'bg-cyan-600/20 text-cyan-400'
                              : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                          }`}
                        >
                          <Icon className="h-5 w-5" />
                          {!isCollapsed && <span className="ml-3">{item.name}</span>}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </nav>
            </div>

            {/* User Info at Bottom - Fixed at the bottom */}
            <div className="p-4 border-t border-slate-700">
              <div className="flex items-center">
                <div className="bg-slate-700 rounded-full w-10 h-10 flex items-center justify-center">
                  <User className="h-5 w-5 text-cyan-400" />
                </div>
                {!isCollapsed && (
                  <div className="ml-3 flex-1 min-w-0">
                    <p className="text-sm font-medium text-white truncate">{user?.email}</p>
                    <button
                      onClick={handleLogout}
                      className="text-xs text-slate-400 hover:text-white mt-1 block w-full text-left"
                    >
                      Logout
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-20 md:hidden"
          onClick={toggleMobileMenu}
        />
      )}
    </>
  );
}