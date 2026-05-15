export interface Notification {
  id: string;
  title?: string;
  body?: string;
  notification_type?: string;
  channel?: string;
  priority?: string;
  is_read: boolean;
  data?: unknown;
  created_at?: string;
}
