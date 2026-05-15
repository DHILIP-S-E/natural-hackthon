export interface QueueEntry {
  id: string;
  customer_name: string;
  customer_phone?: string;
  customer_id?: string;
  service_id?: string;
  preferred_stylist_id?: string;
  position_in_queue: number;
  status: 'waiting' | 'assigned' | 'in_service' | 'completed' | 'left';
  estimated_wait_mins: number;
  walk_in_source?: string;
  joined_queue_at?: string;
  notes?: string;
}
