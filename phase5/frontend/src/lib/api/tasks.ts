import apiClient from '@/lib/api-client';
import { Task } from '@/types/task';
import { normalizeTask, normalizeTasks } from '@/lib/task-utils';

// Define TypeScript interfaces matching the backend models
export interface TaskCreateData {
  title: string;
  description?: string;
  priority?: string; // low, medium, high
  due_date?: string; // ISO date string
  tags?: string; // comma-separated tags
  status?: string; // pending, in progress, completed, archived, cancelled
}

export interface TaskUpdateData {
  title?: string;
  description?: string;
  completed?: boolean;
  priority?: string; // low, medium, high
  due_date?: string; // ISO date string
  tags?: string; // comma-separated tags
  status?: string; // pending, in progress, completed, archived, cancelled
}

// API functions for task operations
// Note: These functions use the authenticated user from the JWT token
export const taskApi = {
  // Create a new task
  createTask: async (taskData: TaskCreateData): Promise<Task> => {
    // Get the current user's ID from localStorage or another source
    // For now, we'll need to get the user ID from the token or profile
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = user.id;

    if (!userId) {
      throw new Error('User not authenticated or user ID not available');
    }

    const response = await apiClient.post<Task>(`/api/${userId}/tasks`, taskData);
    return normalizeTask(response.data);
  },

  // Get all tasks for the authenticated user with optional filtering
  getTasks: async (
    search?: string,
    priority?: string,
    status?: string,
    tags?: string[],
    sortBy: string = "due_date",
    sortOrder: string = "asc"): Promise<Task[]> => {
    // Get the current user's ID from localStorage or another source
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = user.id;

    if (!userId) {
      throw new Error('User not authenticated or user ID not available');
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
  getTaskById: async (taskId: string): Promise<Task> => {
    // Get the current user's ID from localStorage or another source
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = user.id;

    if (!userId) {
      throw new Error('User not authenticated or user ID not available');
    }

    const response = await apiClient.get<Task>(`/api/${userId}/tasks/${taskId}`);
    return normalizeTask(response.data);
  },

  // Update a task
  updateTask: async (taskId: string, taskData: TaskUpdateData): Promise<Task> => {
    // Get the current user's ID from localStorage or another source
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = user.id;

    if (!userId) {
      throw new Error('User not authenticated or user ID not available');
    }

    const response = await apiClient.put<Task>(`/api/${userId}/tasks/${taskId}`, taskData);
    return normalizeTask(response.data);
  },

  // Delete a task
  deleteTask: async (taskId: string): Promise<void> => {
    // Get the current user's ID from localStorage or another source
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = user.id;

    if (!userId) {
      throw new Error('User not authenticated or user ID not available');
    }

    await apiClient.delete(`/api/${userId}/tasks/${taskId}`);
  },

  // Mark a task as complete
  completeTask: async (taskId: string): Promise<Task> => {
    // Get the current user's ID from localStorage or another source
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = user.id;

    if (!userId) {
      throw new Error('User not authenticated or user ID not available');
    }

    const response = await apiClient.patch<Task>(`/api/${userId}/tasks/${taskId}/complete`);
    return normalizeTask(response.data);
  },
};