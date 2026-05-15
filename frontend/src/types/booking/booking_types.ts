export type BookingStatus =
  | 'pending'
  | 'confirmed'
  | 'checked_in'
  | 'in_progress'
  | 'completed'
  | 'cancelled'
  | 'no_show';

export interface Booking {
  id: string;
  booking_number: string;
  customer_id: string;
  location_id: string;
  stylist_id: string;
  service_id: string;
  status: BookingStatus;
  scheduled_at: string;
  base_price: number;
  final_price: number;
  payment_status: string;
  source: string;
  soulskin_session_id?: string;
  notes?: string;
  location_name?: string;
  service_name?: string;
  stylist_name?: string;
}

export interface AvailableSlot {
  time: string;
  stylist_id?: string;
  stylist_name?: string;
}
