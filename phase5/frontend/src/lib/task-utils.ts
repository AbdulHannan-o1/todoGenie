import { Task } from '@/types/task';

/**
 * Derives the completed boolean field from the status field
 * @param task The task object from API response
 * @returns Task with completed field properly set
 */
export const normalizeTask = (task: Partial<Task>): Task => {
  // Ensure completed field is properly set based on status
  const completed = task.status === 'completed';

  return {
    ...task,
    id: task.id || '',
    title: task.title || '',
    description: task.description || '',
    priority: task.priority || 'medium', // Default to 'medium' if not provided, as per backend model
    due_date: task.due_date,
    reminder_time: task.reminder_time,
    tags: task.tags,
    recurrence_pattern: task.recurrence_pattern,
    parent_task_id: task.parent_task_id,
    status: task.status || 'pending',
    created_at: task.created_at || '',
    updated_at: task.updated_at || '',
    user_id: task.user_id || '',
    completed, // Derived from status
  } as Task;
};

/**
 * Normalizes an array of tasks from API response
 * @param tasks Array of tasks from API response
 * @returns Array of normalized tasks with completed field properly set
 */
export const normalizeTasks = (tasks: Partial<Task>[]): Task[] => {
  return tasks.map(normalizeTask);
};

/**
 * Converts a status string to a completed boolean
 * @param status The status string
 * @returns Boolean indicating if the task is completed
 */
export const statusToCompleted = (status: string): boolean => {
  return status === 'completed';
};

/**
 * Converts a completed boolean to a status string
 * @param completed Boolean indicating if the task is completed
 * @returns Status string
 */
export const completedToStatus = (completed: boolean): string => {
  return completed ? 'completed' : 'pending';
};