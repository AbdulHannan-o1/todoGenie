import apiClient from '@/lib/api-client';
import { Tag } from '@/types/task';

// Define TypeScript interfaces matching the backend models
export interface TagCreateData {
  name: string;
  color?: string; // Hex color code
}

export interface TagUpdateData {
  name?: string;
  color?: string; // Hex color code
}

// API functions for tag operations
export const tagApi = {
  // Create a new tag
  createTag: async (tagData: TagCreateData): Promise<Tag> => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = user.id;

    if (!userId) {
      throw new Error('User not authenticated or user ID not available');
    }

    const response = await apiClient.post<Tag>(`/api/tags/`, tagData);
    return response.data;
  },

  // Get all tags for the authenticated user
  getTags: async (): Promise<Tag[]> => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = user.id;

    if (!userId) {
      throw new Error('User not authenticated or user ID not available');
    }

    const response = await apiClient.get<Tag[]>(`/api/tags/`);
    return response.data;
  },

  // Get a specific tag by ID
  getTagById: async (tagId: string): Promise<Tag> => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = user.id;

    if (!userId) {
      throw new Error('User not authenticated or user ID not available');
    }

    const response = await apiClient.get<Tag>(`/api/tags/${tagId}`);
    return response.data;
  },

  // Update a tag
  updateTag: async (tagId: string, tagData: TagUpdateData): Promise<Tag> => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = user.id;

    if (!userId) {
      throw new Error('User not authenticated or user ID not available');
    }

    const response = await apiClient.put<Tag>(`/api/tags/${tagId}`, tagData);
    return response.data;
  },

  // Delete a tag
  deleteTag: async (tagId: string): Promise<void> => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = user.id;

    if (!userId) {
      throw new Error('User not authenticated or user ID not available');
    }

    await apiClient.delete(`/api/tags/${tagId}`);
  },

  // Assign a tag to a task
  assignTagToTask: async (taskId: string, tagId: string): Promise<void> => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = user.id;

    if (!userId) {
      throw new Error('User not authenticated or user ID not available');
    }

    await apiClient.post(`/api/tags/assign/${taskId}/${tagId}`);
  },

  // Remove a tag from a task
  removeTagFromTask: async (taskId: string, tagId: string): Promise<void> => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = user.id;

    if (!userId) {
      throw new Error('User not authenticated or user ID not available');
    }

    await apiClient.post(`/api/tags/remove/${taskId}/${tagId}`);
  },

  // Get tags for a specific task
  getTagsForTask: async (taskId: string): Promise<Tag[]> => {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const userId = user.id;

    if (!userId) {
      throw new Error('User not authenticated or user ID not available');
    }

    const response = await apiClient.get<Tag[]>(`/api/tags/task/${taskId}`);
    return response.data;
  },
};