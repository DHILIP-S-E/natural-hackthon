import { get, post, put } from '../base/api_base';
import type { APIResponse } from '../base/base_type';
import type { Booking } from '../../types/booking/booking_types';

export const bookingsApi = {
  list: (params?: { status?: string; location_id?: string }): Promise<APIResponse<Booking[]>> =>
    get('/bookings', params),

  myBookings: (): Promise<APIResponse<Booking[]>> =>
    get('/bookings/me'),

  getById: (id: string): Promise<APIResponse<Booking>> =>
    get(`/bookings/${id}`),

  create: (data: {
    location_id: string; service_id: string; stylist_id?: string; scheduled_at: string;
    notes?: string; soulskin_session_id?: string;
  }): Promise<APIResponse<Booking>> =>
    post('/bookings', data),

  updateStatus: (id: string, status: string): Promise<APIResponse<Booking>> =>
    put(`/bookings/${id}/status`, { status }),

  cancel: (id: string): Promise<APIResponse<Booking>> =>
    put(`/bookings/${id}/cancel`, {}),

  getAvailableSlots: (params: {
    location_id: string; service_id: string; date: string; stylist_id?: string;
  }): Promise<APIResponse<{ slots: string[] }>> =>
    get('/bookings/available-slots', params),
};
