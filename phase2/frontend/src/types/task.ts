// Define TypeScript interfaces matching the backend models
export interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
  user_id: string; // UUID as string
}