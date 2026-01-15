// Define TypeScript interface matching the backend User model
export interface User {
  id: string; // UUID as string
  email: string;
  username: string;
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
}