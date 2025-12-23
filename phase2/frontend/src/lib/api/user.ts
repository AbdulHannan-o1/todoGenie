import apiClient from '@/lib/api-client';
import { User } from '@/types/user';

// API function to get current user information
export const userApi = {
  // Get current user information using the authenticated token
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/users/me');
    return response.data;
  },
};