import { get, post, put } from '../base/api_base';
import type { APIResponse } from '../base/base_type';
import type { QueueEntry } from '../../types/queue/queue_types';

export const queueApi = {
  list: (locationId: string): Promise<APIResponse<QueueEntry[]>> =>
    get('/queue', { location_id: locationId }),

  add: (data: { customer_name: string; service_id?: string; location_id: string; notes?: string }): Promise<APIResponse<QueueEntry>> =>
    post('/queue', data),

  updateStatus: (id: string, status: string): Promise<APIResponse<QueueEntry>> =>
    put(`/queue/${id}/status`, { status }),

  estimate: (locationId: string): Promise<APIResponse<{ estimated_wait_mins: number; queue_length: number }>> =>
    get('/waittime/estimate', { location_id: locationId }),
};
