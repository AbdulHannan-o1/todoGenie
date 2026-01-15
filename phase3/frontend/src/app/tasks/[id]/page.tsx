"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "../../../components/layout/sidebar";
import { taskApi, TaskUpdateData } from "@/lib/api/tasks";
import { useAuth } from "@/context/auth-context";
import { toast } from "sonner";
import { Menu, Loader2 } from "lucide-react";
import { Task } from "@/types/task";

type EditTaskPageProps = {
  params: {
    id: string;
  };
};

export default function EditTaskPage({ params }: EditTaskPageProps) {
  const { isAuthenticated, user, isLoading } = useAuth();
  const router = useRouter();
  const { id } = React.use(params);
  const taskId = id; // Task IDs are UUIDs, not integers
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    completed: false,
    priority: "medium", // default priority
    due_date: "",
    tags: ""
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  if (isLoading) {
    // Still loading auth state, don't render anything yet
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800 text-white">
        <Loader2 className="h-8 w-8 animate-spin text-cyan-500" />
      </div>
    );
  }

  if (!isAuthenticated) {
    router.push("/login");
    return null;
  }

  useEffect(() => {
    if (!taskId || taskId.length === 0) {
      router.push("/dashboard");
      return;
    }
    fetchTask();
  }, [taskId]);

  const fetchTask = async () => {
    try {
      if (user?.id) {
        const task: Task = await taskApi.getTaskById(taskId);
        setFormData({
          title: task.title,
          description: task.description || "",
          completed: task.completed,
          priority: task.priority || "medium",
          due_date: task.due_date ? new Date(task.due_date).toISOString().slice(0, 16) : "",
          tags: task.tags || ""
        });
      }
    } catch (error) {
      console.error("Error fetching task:", error);
      toast.error("Failed to load task. Redirecting...");
      setTimeout(() => {
        router.push("/dashboard");
      }, 2000);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.title.trim()) {
      toast.error("Title is required");
      return;
    }

    if (!user?.id) {
      toast.error("User not authenticated");
      return;
    }

    setSubmitting(true);
    try {
      await taskApi.updateTask(taskId, {
        title: formData.title, // Required field
        description: formData.description,
        status: formData.completed ? 'completed' : 'pending',
        priority: formData.priority,
        due_date: formData.due_date || undefined, // Send undefined if empty to use backend default
        tags: formData.tags || undefined // Send undefined if empty to use backend default
      });

      toast.success("Task updated successfully!");
      router.push("/dashboard");
    } catch (error) {
      console.error("Error updating task:", error);
      toast.error("Failed to update task. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      completed: e.target.checked,
      status: e.target.checked ? 'completed' : 'pending'
    }));
  };

  if (loading) {
    return (
      <div className="flex min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white">
        <div className="flex items-center justify-center flex-1">
          <Loader2 className="h-8 w-8 animate-spin text-cyan-500" />
        </div>
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
              <h1 className="text-2xl font-bold">Edit Task</h1>
            </div>
          </div>
        </header>

        <div className="p-6 max-w-2xl mx-auto">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-slate-300 mb-2">
                Title *
              </label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                placeholder="Enter task title"
                className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                required
              />
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-slate-300 mb-2">
                Description
              </label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Enter task description (optional)"
                rows={4}
                className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 resize-none"
              />
            </div>

            <div>
              <label htmlFor="priority" className="block text-sm font-medium text-slate-300 mb-2">
                Priority
              </label>
              <select
                id="priority"
                name="priority"
                value={formData.priority}
                onChange={handleInputChange}
                className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-1 focus:ring-cyan-500"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            <div>
              <label htmlFor="due_date" className="block text-sm font-medium text-slate-300 mb-2">
                Due Date (Optional)
              </label>
              <input
                type="datetime-local"
                id="due_date"
                name="due_date"
                value={formData.due_date}
                onChange={handleInputChange}
                className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2 text-white placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
              />
            </div>

            <div>
              <label htmlFor="tags" className="block text-sm font-medium text-slate-300 mb-2">
                Tags (comma-separated, optional)
              </label>
              <input
                type="text"
                id="tags"
                name="tags"
                value={formData.tags}
                onChange={handleInputChange}
                placeholder="work, personal, urgent"
                className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2 text-white placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
              />
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="completed"
                name="completed"
                checked={formData.completed}
                onChange={handleCheckboxChange}
                className="h-4 w-4 rounded border-slate-600 bg-slate-700 text-cyan-600 focus:ring-cyan-500"
              />
              <label htmlFor="completed" className="ml-2 text-sm text-slate-300">
                Mark as completed
              </label>
            </div>

            <div className="flex space-x-4 pt-4">
              <button
                type="submit"
                disabled={submitting}
                className="flex items-center bg-cyan-600 hover:bg-cyan-700 text-white px-6 py-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Updating...
                  </>
                ) : (
                  "Update Task"
                )}
              </button>
              <button
                type="button"
                onClick={() => router.push("/dashboard")}
                className="bg-slate-700 hover:bg-slate-600 text-white px-6 py-3 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}