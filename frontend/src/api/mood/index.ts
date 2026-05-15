import { get, post } from '../base/api_base';
import type { APIResponse } from '../base/base_type';
import type { MoodDetection } from '../../types/mood/mood_types';

export const moodApi = {
  detect: (data: { customer_id: string; image_data?: string; context?: string }): Promise<APIResponse<MoodDetection>> =>
    post('/mood/detect', data),

  history: (customerId: string): Promise<APIResponse<MoodDetection[]>> =>
    get('/mood/history', { customer_id: customerId }),

  latest: (customerId: string): Promise<APIResponse<MoodDetection>> =>
    get('/mood/latest', { customer_id: customerId }),
};
