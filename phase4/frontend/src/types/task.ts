// Define TypeScript interfaces matching the backend models
export interface Task {
  id: string; // UUID as string
  title: string;
  description?: string;
  completed: boolean; // Derived from status field for UI convenience
  priority: string; // low, medium, high
  due_date?: string; // ISO date string
  tags?: string; // comma-separated tags
  status: string; // pending, in progress, completed, archived, cancelled
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
  user_id: string; // UUID as string
}