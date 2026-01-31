"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "../../../components/layout/sidebar";
import { taskApi, TaskUpdateData } from "@/lib/api/tasks";
import { useAuth } from "@/context/auth-context";
import { toast } from "sonner";
import { Menu, Loader2, Clock, Repeat, FolderTree } from "lucide-react";
import { Task } from "@/types/task";

type EditTaskPageProps = {
  params: {
    id: string;
  };
};

export default function EditTaskPage({ params }: EditTaskPageProps) {
  const { isAuthenticated, user, isLoading } = useAuth();
  const router = useRouter();
  const { id } = params;
  const taskId = id; // Task IDs are UUIDs, not integers
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [formData, setFormData] = useState<{
    title: string;
    description: string;
    completed: boolean;
    priority: string;
    due_date: string;
    reminder_time: string;
    tags: string;
    recurrence_pattern: {
      frequency: string;
      interval: number;
      end_condition: {
        type: string;
        value?: string | number;
      };
      exceptions: string[];
    };
    parent_task_id: string;
  }>({
    title: "",
    description: "",
    completed: false,
    priority: "medium", // default priority
    due_date: "",
    reminder_time: "",
    tags: "",
    recurrence_pattern: {
      frequency: "none",
      interval: 1,
      end_condition: {
        type: "never",
        value: undefined
      },
      exceptions: []
    },
    parent_task_id: ""
  });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (isLoading) {
      // Still loading auth state, don't proceed yet
      return;
    }
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    if (!taskId || taskId.length === 0) {
      router.push("/dashboard");
      return;
    }
    fetchTask();
  }, [taskId, isLoading, isAuthenticated]);

  // Render loading state while auth is loading
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800 text-white">
        <Loader2 className="h-8 w-8 animate-spin text-cyan-500" />
      </div>
    );
  }

  // Render login redirect after useEffect has had a chance to run
  if (!isAuthenticated) {
    // This will be handled by the useEffect, so just render nothing or a loader
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800 text-white">
        Redirecting to login...
      </div>
    );
  }

  const fetchTask = async () => {
    try {
      if (user?.id) {
        const task: Task = await taskApi.getTaskById(user.id, taskId);
        setFormData({
          title: task.title,
          description: task.description || "",
          completed: task.completed,
          priority: task.priority || "medium",
          due_date: task.due_date ? new Date(task.due_date).toISOString().slice(0, 16) : "",
          reminder_time: task.reminder_time ? new Date(task.reminder_time).toISOString().slice(0, 16) : "",
          tags: task.tags || "",
          recurrence_pattern: task.recurrence_pattern ? {
            frequency: task.recurrence_pattern.frequency,
            interval: task.recurrence_pattern.interval,
            end_condition: {
              type: task.recurrence_pattern.end_condition.type,
              value: task.recurrence_pattern.end_condition.value
            },
            exceptions: task.recurrence_pattern.exceptions || []
          } : {
            frequency: "none",
            interval: 1,
            end_condition: {
              type: "never",
              value: undefined
            },
            exceptions: []
          },
          parent_task_id: task.parent_task_id || ""
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
      // Prepare recurrence pattern - only include if recurrence is enabled
      const recurrencePattern = formData.recurrence_pattern.frequency !== "none" ? {
        frequency: formData.recurrence_pattern.frequency as 'daily' | 'weekly' | 'monthly' | 'yearly' | 'custom',
        interval: formData.recurrence_pattern.interval,
        end_condition: {
          type: formData.recurrence_pattern.end_condition.type as 'never' | 'on_date' | 'after_occurrences',
          value: formData.recurrence_pattern.end_condition.value
        },
        exceptions: formData.recurrence_pattern.exceptions || []
      } : undefined;

      await taskApi.updateTask(user.id, taskId, {
        title: formData.title, // Required field
        description: formData.description,
        status: formData.completed ? 'completed' : 'pending',
        priority: formData.priority,
        due_date: formData.due_date || undefined, // Send undefined if empty to use backend default
        reminder_time: formData.reminder_time || undefined,
        tags: formData.tags || undefined, // Send undefined if empty to use backend default
        recurrence_pattern: recurrencePattern,
        parent_task_id: formData.parent_task_id || undefined
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

  const handleRecurrenceChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
    const { name, value } = e.target;

    if (name.startsWith('end_condition')) {
      // Handle nested end_condition changes
      const endConditionField = name.split('.')[1];
      setFormData(prev => ({
        ...prev,
        recurrence_pattern: {
          ...prev.recurrence_pattern,
          end_condition: {
            ...prev.recurrence_pattern.end_condition,
            [endConditionField]: value
          }
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        recurrence_pattern: {
          ...prev.recurrence_pattern,
          [name]: name === 'interval' ? parseInt(value) : value
        }
      }));
    }
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

            {/* Advanced Options Section */}
            <div className="border-t border-slate-700 pt-6 mt-6">
              <h3 className="text-lg font-medium text-slate-300 mb-4">Advanced Options</h3>

              {/* Reminder Time */}
              <div className="mb-4">
                <label htmlFor="reminder_time" className="block text-sm font-medium text-slate-300 mb-2 flex items-center">
                  <Clock className="h-4 w-4 mr-2" />
                  Reminder Time (Optional)
                </label>
                <input
                  type="datetime-local"
                  id="reminder_time"
                  name="reminder_time"
                  value={formData.reminder_time}
                  onChange={handleInputChange}
                  className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2 text-white placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                />
              </div>

              {/* Recurrence Pattern */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-300 mb-2 flex items-center">
                  <Repeat className="h-4 w-4 mr-2" />
                  Recurrence Pattern (Optional)
                </label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label htmlFor="frequency" className="block text-xs text-slate-400 mb-1">Frequency</label>
                    <select
                      id="frequency"
                      name="frequency"
                      value={formData.recurrence_pattern.frequency}
                      onChange={handleRecurrenceChange}
                      className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-cyan-500"
                    >
                      <option value="none">None</option>
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                      <option value="monthly">Monthly</option>
                      <option value="yearly">Yearly</option>
                      <option value="custom">Custom</option>
                    </select>
                  </div>
                  <div>
                    <label htmlFor="interval" className="block text-xs text-slate-400 mb-1">Interval</label>
                    <input
                      type="number"
                      id="interval"
                      name="interval"
                      min="1"
                      value={formData.recurrence_pattern.interval}
                      onChange={handleRecurrenceChange}
                      disabled={formData.recurrence_pattern.frequency === "none"}
                      className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-cyan-500 disabled:opacity-50"
                    />
                  </div>
                  <div>
                    <label htmlFor="end_condition.type" className="block text-xs text-slate-400 mb-1">End Condition</label>
                    <select
                      id="end_condition.type"
                      name="end_condition.type"
                      value={formData.recurrence_pattern.end_condition.type}
                      onChange={handleRecurrenceChange}
                      disabled={formData.recurrence_pattern.frequency === "none"}
                      className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-cyan-500 disabled:opacity-50"
                    >
                      <option value="never">Never</option>
                      <option value="on_date">On Date</option>
                      <option value="after_occurrences">After Occurrences</option>
                    </select>
                  </div>
                </div>

                {formData.recurrence_pattern.end_condition.type !== "never" && formData.recurrence_pattern.frequency !== "none" && (
                  <div className="mt-3">
                    <label htmlFor="end_condition.value" className="block text-xs text-slate-400 mb-1">
                      {formData.recurrence_pattern.end_condition.type === "on_date"
                        ? "End Date"
                        : "Number of Occurrences"}
                    </label>
                    {formData.recurrence_pattern.end_condition.type === "on_date" ? (
                      <input
                        type="date"
                        id="end_condition.value"
                        name="end_condition.value"
                        value={typeof formData.recurrence_pattern.end_condition.value === 'string' ? formData.recurrence_pattern.end_condition.value : ''}
                        onChange={handleRecurrenceChange}
                        className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-cyan-500"
                      />
                    ) : (
                      <input
                        type="number"
                        id="end_condition.value"
                        name="end_condition.value"
                        min="1"
                        value={typeof formData.recurrence_pattern.end_condition.value === 'number' ? formData.recurrence_pattern.end_condition.value : ''}
                        onChange={handleRecurrenceChange}
                        className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-1 focus:ring-cyan-500"
                      />
                    )}
                  </div>
                )}
              </div>

              {/* Parent Task */}
              <div>
                <label htmlFor="parent_task_id" className="block text-sm font-medium text-slate-300 mb-2 flex items-center">
                  <FolderTree className="h-4 w-4 mr-2" />
                  Parent Task (Optional)
                </label>
                <input
                  type="text"
                  id="parent_task_id"
                  name="parent_task_id"
                  value={formData.parent_task_id}
                  onChange={handleInputChange}
                  placeholder="Enter parent task ID for hierarchical tasks"
                  className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2 text-white placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                />
              </div>
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