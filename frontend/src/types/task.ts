export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  created_at: string;
  completed_at?: string;
  priority?: "low" | "medium" | "high" | "urgent";
  tags?: string[];
  due_date?: string;
  reminder_lead_time?: number;
  recurrence_rule?: string;
  recurrence_parent_id?: string;
}
