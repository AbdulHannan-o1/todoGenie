'use client';

import { Task } from '@/types/task';
import { Clock, Repeat, Tag, FolderTree, Calendar, Bell } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { taskApi } from '@/lib/api/tasks';

interface TaskDetailsModalProps {
  task: Task | null;
  isOpen: boolean;
  onClose: () => void;
  onEdit: () => void;
}

export default function TaskDetailsModal({
  task,
  isOpen,
  onClose,
  onEdit
}: TaskDetailsModalProps) {
  const router = useRouter();
  const [childTasks, setChildTasks] = useState<Task[]>([]);

  useEffect(() => {
    if (task && isOpen) {
      // Fetch child tasks for this task
      const fetchChildTasks = async () => {
        try {
          // Get user ID from localStorage
          const user = JSON.parse(localStorage.getItem('user') || '{}');
          if (user.id) {
            const childTasksData = await taskApi.getChildTasks(user.id, task.id);
            setChildTasks(childTasksData);
          }
        } catch (error) {
          console.error('Error fetching child tasks:', error);
          setChildTasks([]); // Set to empty array on error
        }
      };

      fetchChildTasks();
    } else {
      // Reset child tasks when modal is closed or task changes
      setChildTasks([]);
    }
  }, [task, isOpen]);

  if (!task) return null;

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Not set';
    try {
      return new Date(dateString).toLocaleString();
    } catch (e) {
      return 'Invalid date';
    }
  };

  if (!task) return null;

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="sm:max-w-md max-h-[80vh] overflow-y-auto bg-slate-800 border border-slate-700 rounded-xl p-6 w-full mx-4 max-w-2xl">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-xl font-bold text-white">
                Task Details
              </h2>
              <button
                onClick={onClose}
                className="text-slate-400 hover:text-white text-xl"
              >
                &times;
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-slate-300 mb-1">Title</h3>
                <p className="text-white">{task.title}</p>
              </div>

              {task.description && (
                <div>
                  <h3 className="font-semibold text-slate-300 mb-1">Description</h3>
                  <p className="text-slate-300 whitespace-pre-wrap">{task.description}</p>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold text-slate-300 mb-1">Status</h3>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    task.status === 'completed'
                      ? "bg-green-500/20 text-green-400"
                      : "bg-yellow-500/20 text-yellow-400"
                  }`}>
                    {task.status}
                  </span>
                </div>

                <div>
                  <h3 className="font-semibold text-slate-300 mb-1">Priority</h3>
                  <span
                    className={
                      `inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      task.priority === 'high' ? 'bg-red-500/20 text-red-400' :
                      task.priority === 'urgent' ? 'bg-red-600/30 text-red-300' :
                      task.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-green-500/20 text-green-400'}`}
                  >
                    {task.priority}
                  </span>
                </div>
              </div>

              {task.due_date && (
                <div className="flex items-center text-slate-300">
                  <Calendar className="h-4 w-4 mr-2" />
                  <span className="font-semibold mr-2">Due Date:</span>
                  <span>{formatDate(task.due_date)}</span>
                </div>
              )}

              {task.reminder_time && (
                <div className="flex items-center text-slate-300">
                  <Bell className="h-4 w-4 mr-2" />
                  <span className="font-semibold mr-2">Reminder:</span>
                  <span>{formatDate(task.reminder_time)}</span>
                </div>
              )}

              {task.recurrence_pattern && task.recurrence_pattern.frequency !== 'none' && (
                <div className="flex items-center text-slate-300">
                  <Repeat className="h-4 w-4 mr-2" />
                  <span className="font-semibold mr-2">Recurrence:</span>
                  <span>
                    {task.recurrence_pattern.interval > 1
                      ? `${task.recurrence_pattern.interval} ${task.recurrence_pattern.frequency}s`
                      : task.recurrence_pattern.frequency}
                  </span>
                </div>
              )}

              {task.tags && task.tags.trim() !== '' && (
                <div className="flex items-center text-slate-300">
                  <Tag className="h-4 w-4 mr-2" />
                  <span className="font-semibold mr-2">Tags:</span>
                  <div className="flex flex-wrap gap-1">
                    {task.tags.split(',').map((tag, index) => (
                      <span key={index} className="text-xs px-2 py-1 rounded-full bg-slate-700 text-slate-300 border border-slate-600">
                        {tag.trim()}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {task.parent_task_id && (
                <div className="flex items-center text-slate-300">
                  <FolderTree className="h-4 w-4 mr-2" />
                  <span className="font-semibold mr-2">Parent Task:</span>
                  <span>ID: {task.parent_task_id}</span>
                </div>
              )}

              {/* Child tasks section */}
              {childTasks.length > 0 && (
                <div className="pt-4 border-t border-slate-700">
                  <h3 className="font-semibold text-slate-300 mb-2">Child Tasks ({childTasks.length})</h3>
                  <div className="space-y-2">
                    {childTasks.map((childTask) => (
                      <div key={childTask.id} className="flex items-center justify-between p-2 bg-slate-700/50 rounded">
                        <span className="text-slate-300">{childTask.title}</span>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          childTask.status === 'completed'
                            ? "bg-green-500/20 text-green-400"
                            : "bg-yellow-500/20 text-yellow-400"
                        }`}>
                          {childTask.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="flex space-x-2 mt-6">
              <button
                onClick={onEdit}
                className="flex-1 bg-cyan-600 hover:bg-cyan-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Edit Task
              </button>
              <button
                onClick={onClose}
                className="flex-1 border border-slate-600 text-slate-300 hover:bg-slate-700 px-4 py-2 rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}