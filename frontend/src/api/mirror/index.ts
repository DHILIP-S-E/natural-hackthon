import { get, post } from '../base/api_base';
import type { APIResponse } from '../base/base_type';

export interface ARTryOn {
  id: string; customer_id: string; style_id?: string; result_url?: string; created_at: string;
}

export const mirrorApi = {
  tryOn: (data: { customer_id: string; style_id: string; image_data?: string }): Promise<APIResponse<ARTryOn>> =>
    post('/mirror/try-on', data),

  history: (customerId: string): Promise<APIResponse<ARTryOn[]>> =>
    get('/mirror/history', { customer_id: customerId }),

  styles: (params?: { category?: string }): Promise<APIResponse<unknown[]>> =>
    get('/mirror/styles', params),
};
