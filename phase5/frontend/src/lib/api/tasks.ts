import apiClient from '@/lib/api-client';
import { Task } from '@/types/task';
import { normalizeTask, normalizeTasks } from '@/lib/task-utils';

// Define TypeScript interfaces matching the backend models
export interface TaskCreateData {
  title: string;
  description?: string;
  priority?: string; // low, medium, high, urgent
  due_date?: string; // ISO date string
  reminder_time?: string; // ISO date string for reminder
  tags?: string; // comma-separated tags
  recurrence_pattern?: RecurrencePattern; // Recurrence pattern for recurring tasks
  parent_task_id?: string; // UUID as string for hierarchical tasks
  status?: string; // pending, in progress, completed, archived, cancelled
}

export interface TaskUpdateData {
  title?: string;
  description?: string;
  completed?: boolean;
  priority?: string; // low, medium, high, urgent
  due_date?: string; // ISO date string
  reminder_time?: string; // ISO date string for reminder
  tags?: string; // comma-separated tags
  recurrence_pattern?: RecurrencePattern; // Recurrence pattern for recurring tasks
  parent_task_id?: string; // UUID as string for hierarchical tasks
  status?: string; // pending, in progress, completed, archived, cancelled
}

export interface RecurrencePattern {
  frequency: 'daily' | 'weekly' | 'monthly' | 'yearly' | 'custom'; // Recurrence frequency
  interval: number; // Interval multiplier (e.g., every 2 weeks)
  end_condition: {
    type: 'never' | 'on_date' | 'after_occurrences'; // When to stop recurrence
    value?: string | number; // Date string or occurrence count
  };
  exceptions?: string[]; // Array of dates to skip in recurrence
}

// API functions for task operations
// Note: These functions use the authenticated user from the JWT token
export const taskApi = {
  // Create a new task
  createTask: async (userId: string, taskData: TaskCreateData): Promise<Task> => {
    if (!userId) {
      throw new Error('User ID is required');
    }

    const response = await apiClient.post<Task>(`/api/${userId}/tasks`, taskData);
    return normalizeTask(response.data);
  },

  // Get all tasks for the authenticated user with optional filtering
  getTasks: async (
    userId: string,
    search?: string,
    priority?: string,
    status?: string,
    tags?: string[],
    sortBy: string = "due_date",
    sortOrder: string = "asc"): Promise<Task[]> => {
    if (!userId) {
      throw new Error('User ID is required');
    }

    // Build query parameters
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (priority) params.append('priority', priority);
    if (status) params.append('status', status);
    if (tags) tags.forEach(tag => params.append('tags', tag));
    params.append('sort_by', sortBy);
    params.append('sort_order', sortOrder);

    const queryString = params.toString();
    const url = `/api/${userId}/tasks${queryString ? '?' + queryString : ''}`;

    const response = await apiClient.get<Task[]>(url);
    return normalizeTasks(response.data);
  },

  // Get a specific task by ID
  getTaskById: async (userId: string, taskId: string): Promise<Task> => {
    if (!userId) {
      throw new Error('User ID is required');
    }

    const response = await apiClient.get<Task>(`/api/${userId}/tasks/${taskId}`);
    return normalizeTask(response.data);
  },

  // Update a task
  updateTask: async (userId: string, taskId: string, taskData: TaskUpdateData): Promise<Task> => {
    if (!userId) {
      throw new Error('User ID is required');
    }

    const response = await apiClient.put<Task>(`/api/${userId}/tasks/${taskId}`, taskData);
    return normalizeTask(response.data);
  },

  // Delete a task
  deleteTask: async (userId: string, taskId: string): Promise<void> => {
    if (!userId) {
      throw new Error('User ID is required');
    }

    await apiClient.delete(`/api/${userId}/tasks/${taskId}`);
  },

  // Mark a task as complete
  completeTask: async (userId: string, taskId: string): Promise<Task> => {
    if (!userId) {
      throw new Error('User ID is required');
    }

    const response = await apiClient.patch<Task>(`/api/${userId}/tasks/${taskId}/complete`);
    return normalizeTask(response.data);
  },

  // Get child tasks for a parent task
  getChildTasks: async (userId: string, taskId: string): Promise<Task[]> => {
    if (!userId) {
      throw new Error('User ID is required');
    }

    const response = await apiClient.get<Task[]>(`/api/${userId}/tasks/${taskId}/children`);
    return normalizeTasks(response.data);
  },

  // Create a child task under a parent task
  createChildTask: async (userId: string, taskId: string, taskData: TaskCreateData): Promise<Task> => {
    if (!userId) {
      throw new Error('User ID is required');
    }

    const response = await apiClient.post<Task>(`/api/${userId}/tasks/${taskId}/children`, taskData);
    return normalizeTask(response.data);
  },

  // Get parent tasks (ancestors) for a task
  getParentTasks: async (userId: string, taskId: string): Promise<Task[]> => {
    if (!userId) {
      throw new Error('User ID is required');
    }

    const response = await apiClient.get<Task[]>(`/api/${userId}/tasks/${taskId}/ancestors`);
    return normalizeTasks(response.data);
  },

  // Get upcoming reminders for a user
  getUpcomingReminders: async (userId: string, hoursAhead: number = 24): Promise<any[]> => {
    if (!userId) {
      throw new Error('User ID is required');
    }

    const response = await apiClient.get<any[]>(`/api/${userId}/tasks/reminders/upcoming?hours_ahead=${hoursAhead}`);
    return response.data;
  },
};