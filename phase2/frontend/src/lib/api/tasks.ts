import apiClient from '@/lib/api-client';
import { Task } from '@/types/task';

// Define the API endpoints based on the backend structure
const TASKS_API_BASE = '/api/tasks';

// Define TypeScript interfaces matching the backend models
export interface TaskCreateData {
  title: string;
  description?: string;
}

export interface TaskUpdateData {
  title?: string;
  description?: string;
  completed?: boolean;
}

// API functions for task operations
export const taskApi = {
  // Create a new task
  createTask: async (taskData: TaskCreateData): Promise<Task> => {
    const response = await apiClient.post<Task>(TASKS_API_BASE, taskData);
    return response.data;
  },

  // Get all tasks for the authenticated user
  getTasks: async (): Promise<Task[]> => {
    const response = await apiClient.get<Task[]>(TASKS_API_BASE);
    return response.data;
  },

  // Get a specific task by ID
  getTaskById: async (taskId: number): Promise<Task> => {
    const response = await apiClient.get<Task>(`${TASKS_API_BASE}/${taskId}`);
    return response.data;
  },

  // Update a task
  updateTask: async (taskId: number, taskData: TaskUpdateData): Promise<Task> => {
    const response = await apiClient.put<Task>(`${TASKS_API_BASE}/${taskId}`, taskData);
    return response.data;
  },

  // Delete a task
  deleteTask: async (taskId: number): Promise<void> => {
    await apiClient.delete(`${TASKS_API_BASE}/${taskId}`);
  },
};