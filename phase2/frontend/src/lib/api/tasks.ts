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
// Note: These functions need the userId to be passed from the calling component
export const taskApi = {
  // Create a new task
  createTask: async (taskData: TaskCreateData, userId: string): Promise<Task> => {
    const response = await apiClient.post<Task>(`/${userId}/tasks`, taskData);
    return normalizeTask(response.data);
  },

  // Get all tasks for the authenticated user with optional filtering
  getTasks: async (userId: string,
    search?: string,
    priority?: string,
    status?: string,
    tags?: string[],
    sortBy: string = "due_date",
    sortOrder: string = "asc"): Promise<Task[]> => {
    // Build query parameters
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (priority) params.append('priority', priority);
    if (status) params.append('status', status);
    if (tags) tags.forEach(tag => params.append('tags', tag));
    params.append('sort_by', sortBy);
    params.append('sort_order', sortOrder);

    const queryString = params.toString();
    const url = `/${userId}/tasks${queryString ? '?' + queryString : ''}`;

    const response = await apiClient.get<Task[]>(url);
    return normalizeTasks(response.data);
  },

  // Get a specific task by ID
  getTaskById: async (userId: string, taskId: string): Promise<Task> => {
    const response = await apiClient.get<Task>(`/${userId}/tasks/${taskId}`);
    return normalizeTask(response.data);
  },

  // Update a task
  updateTask: async (userId: string, taskId: string, taskData: TaskUpdateData): Promise<Task> => {
    const response = await apiClient.put<Task>(`/${userId}/tasks/${taskId}`, taskData);
    return normalizeTask(response.data);
  },

  // Delete a task
  deleteTask: async (userId: string, taskId: string): Promise<void> => {
    await apiClient.delete(`/${userId}/tasks/${taskId}`);
  },

  // Mark a task as complete
  completeTask: async (userId: string, taskId: string): Promise<Task> => {
    const response = await apiClient.patch<Task>(`/${userId}/tasks/${taskId}/complete`);
    return normalizeTask(response.data);
  },
};