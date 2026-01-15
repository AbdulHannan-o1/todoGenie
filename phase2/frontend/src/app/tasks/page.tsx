"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/context/auth-context";
import { useRouter } from "next/navigation";
import Sidebar from "../../components/layout/sidebar";
import { taskApi } from "@/lib/api/tasks";
import { Task } from "@/types/task";
import { Menu, Plus, Search, Filter, Calendar, CheckCircle, Clock, ListTodo, AlertCircle, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

export default function TasksPage() {
  const { isAuthenticated, user, isLoading } = useAuth();
  const router = useRouter();
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [priorityFilter, setPriorityFilter] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    if (isLoading) {
      // Still loading auth state, don't redirect yet
      return;
    }
    if (!isAuthenticated) {
      router.push("/login");
    } else {
      fetchTasks();
    }
  }, [isAuthenticated, isLoading]);

  useEffect(() => {
    if (isAuthenticated && user?.id) {
      fetchTasks();
    }
  }, [searchTerm, priorityFilter, statusFilter, isAuthenticated, user?.id]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      if (user?.id) {
        const tasksData = await taskApi.getTasks(
          user.id,
          searchTerm || undefined,
          priorityFilter || undefined,
          statusFilter || undefined
        );
        setTasks(tasksData);
      }
    } catch (error) {
      console.error("Error fetching tasks:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleTaskStatusChange = async (task: Task) => {
    try {
      if (user?.id) {
        // Toggle the status based on current state
        const newStatus = task.status === 'completed' ? 'pending' : 'completed';

        // Update the task with the new status, including required fields
        const updatedTask = await taskApi.updateTask(user.id, task.id, {
          title: task.title, // Required field
          status: newStatus
        });

        // Update the task in the local state
        setTasks(prevTasks =>
          prevTasks.map(t =>
            t.id === updatedTask.id ? updatedTask : t
          )
        );
      }
    } catch (error) {
      console.error("Error updating task:", error);
      // If the API call failed, refetch tasks to ensure UI is in sync with server
      fetchTasks();
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      if (user?.id) {
        await taskApi.deleteTask(user.id, taskId);
        setTasks(tasks.filter(task => task.id !== taskId));
      }
    } catch (error) {
      console.error("Error deleting task:", error);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800 text-white">
        Loading or redirecting...
      </div>
    );
  }

  // Calculate stats based on tasks
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(task => task.status === 'completed').length;
  const pendingTasks = totalTasks - completedTasks;
  const overdueTasks = 0; // This would require date comparison in a real implementation

  const stats = [
    { title: "Total Tasks", value: totalTasks.toString(), icon: ListTodo, color: "text-cyan-500" },
    { title: "Completed", value: completedTasks.toString(), icon: CheckCircle, color: "text-green-500" },
    { title: "Pending", value: pendingTasks.toString(), icon: Clock, color: "text-yellow-500" },
    { title: "Overdue", value: overdueTasks.toString(), icon: AlertCircle, color: "text-red-500" },
  ];

  // Use tasks from state since they are already filtered by the API
  const filteredTasks = tasks;

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
                <h1 className="text-2xl font-bold">Tasks</h1>
                <p className="text-slate-400 text-sm">Manage your tasks efficiently</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 h-4 w-4" />
                <input
                  type="text"
                  placeholder="Search tasks..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="bg-slate-700/50 border border-slate-600 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                />
              </div>

              <button
                className="p-2 rounded-lg bg-slate-700/50 hover:bg-slate-700 transition-colors"
                onClick={() => setShowFilters(!showFilters)}
              >
                <Filter className="h-5 w-5 text-slate-300" />
              </button>

              <button
                className="flex items-center bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg transition-colors"
                onClick={() => router.push('/tasks/new')}
              >
                <Plus className="h-4 w-4 mr-2" />
                New Task
              </button>
            </div>
          </div>
        </header>

        {/* Stats Section */}
        <section className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={index}
                  className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl p-6"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-slate-400 text-sm">{stat.title}</p>
                      <p className="text-2xl font-bold mt-1">{stat.value}</p>
                    </div>
                    <div className={`p-3 rounded-lg bg-slate-700 ${stat.color}`}>
                      <Icon className="h-6 w-6" />
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Task List */}
          <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-xl overflow-hidden">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <Loader2 className="h-8 w-8 animate-spin text-cyan-500" />
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-700/50 border-b border-slate-700">
                    <tr>
                      <th className="text-left py-3 px-4 font-medium text-slate-300">Task</th>
                      <th className="text-left py-3 px-4 font-medium text-slate-300">Status</th>
                      <th className="text-left py-3 px-4 font-medium text-slate-300">Due Date</th>
                      <th className="text-left py-3 px-4 font-medium text-slate-300">Created</th>
                      <th className="text-left py-3 px-4 font-medium text-slate-300">Updated</th>
                      <th className="text-left py-3 px-4 font-medium text-slate-300">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredTasks.length > 0 ? (
                      filteredTasks.map((task) => (
                        <motion.tr
                          key={task.id}
                          className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ duration: 0.3 }}
                        >
                          <td className="py-3 px-4">
                            <div className="flex items-center">
                              <input
                                type="checkbox"
                                checked={task.status === 'completed'}
                                onChange={() => handleTaskStatusChange(task)}
                                className="h-4 w-4 rounded border-slate-600 bg-slate-700 text-cyan-600 focus:ring-cyan-500"
                              />
                              <div className="ml-3">
                                <span className={`${task.status === 'completed' ? "line-through text-slate-500" : "text-white"}`}>
                                  {task.title}
                                </span>
                                <span className={`ml-2 text-xs px-2 py-1 rounded-full ${
                                  task.priority === 'high' ? 'bg-red-500/20 text-red-400' :
                                  task.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                                  'bg-green-500/20 text-green-400'
                                }`}>
                                  {task.priority}
                                </span>
                              </div>
                            </div>
                            {task.description && (
                              <p className="text-sm text-slate-400 ml-7 mt-1">{task.description}</p>
                            )}
                          </td>
                          <td className="py-3 px-4">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              task.status === 'completed'
                                ? "bg-green-500/20 text-green-400"
                                : "bg-yellow-500/20 text-yellow-400"
                            }`}>
                              {task.status === 'completed' ? "Completed" : "Pending"}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-slate-300">
                            {task.due_date ? (() => {
                              try {
                                return new Date(task.due_date).toLocaleDateString();
                              } catch (e) {
                                return 'N/A';
                              }
                            })() : 'N/A'}
                          </td>
                          <td className="py-3 px-4 text-slate-300">
                            {task.created_at ? (() => {
                              try {
                                return new Date(task.created_at).toLocaleDateString();
                              } catch (e) {
                                return 'N/A';
                              }
                            })() : 'N/A'}
                          </td>
                          <td className="py-3 px-4 text-slate-300">
                            {task.updated_at ? (() => {
                              try {
                                return new Date(task.updated_at).toLocaleDateString();
                              } catch (e) {
                                return 'N/A';
                              }
                            })() : 'N/A'}
                          </td>
                          <td className="py-3 px-4">
                            <button
                              onClick={() => router.push(`/tasks/${task.id}`)}
                              className="text-slate-400 hover:text-cyan-400 mr-3"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => handleDeleteTask(task.id)}
                              className="text-slate-400 hover:text-red-400"
                            >
                              Delete
                            </button>
                          </td>
                        </motion.tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={6} className="py-8 px-4 text-center text-slate-500">
                          No tasks found. Create your first task to get started!
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}