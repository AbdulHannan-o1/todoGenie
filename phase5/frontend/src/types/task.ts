// Define TypeScript interfaces matching the backend models
export interface Task {
  id: string; // UUID as string
  title: string;
  description?: string;
  completed: boolean; // Derived from status field for UI convenience
  priority: string; // low, medium, high, urgent
  due_date?: string; // ISO date string
  reminder_time?: string; // ISO date string for reminder
  tags?: string; // comma-separated tags
  recurrence_pattern?: RecurrencePattern; // Recurrence pattern for recurring tasks
  parent_task_id?: string; // UUID as string for hierarchical tasks
  status: string; // pending, in progress, completed, archived, cancelled
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
  user_id: string; // UUID as string
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

export interface Tag {
  id: string; // UUID as string
  name: string;
  color?: string; // Hex color code
  user_id: string; // UUID as string
  created_at: string; // ISO date string
  updated_at: string; // ISO date string
}

export interface Notification {
  id: string; // UUID as string
  user_id: string; // UUID as string
  task_id?: string; // UUID as string, optional for system notifications
  type: string; // reminder, recurring_task_created, system_alert
  message: string;
  scheduled_time: string; // ISO date string
  sent_time?: string; // ISO date string
  status: string; // scheduled, sent, failed, cancelled
  created_at: string; // ISO date string
}