"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "../../../components/layout/sidebar";
import { taskApi, TaskUpdateData } from "@/lib/api/tasks";
import { useAuth } from "@/context/auth-context";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";
import { Task } from "@/types/task";

type EditTaskPageProps = {
  params: {
    id: string;
  };
};

export default function EditTaskPage({ params }: EditTaskPageProps) {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const { id } = params;
  const taskId = parseInt(id, 10);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    completed: false
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  if (!isAuthenticated) {
    router.push("/login");
    return null;
  }

  useEffect(() => {
    if (isNaN(taskId) || taskId <= 0) {
      router.push("/dashboard");
      return;
    }
    fetchTask();
  }, [taskId]);

  const fetchTask = async () => {
    try {
      const task: Task = await taskApi.getTaskById(taskId);
      setFormData({
        title: task.title,
        description: task.description || "",
        completed: task.completed
      });
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

    setSubmitting(true);
    try {
      await taskApi.updateTask(taskId, {
        title: formData.title,
        description: formData.description,
        completed: formData.completed
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

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      completed: e.target.checked
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
            <h1 className="text-2xl font-bold">Edit Task</h1>
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