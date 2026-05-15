import { get, post, put } from '../base/api_base';
import type { APIResponse } from '../base/base_type';
import type { TrainingRecord } from '../../types/training/training_types';

export const trainingApi = {
  myRecords: (): Promise<APIResponse<TrainingRecord[]>> =>
    get('/training/me'),

  list: (params?: { staff_id?: string; location_id?: string }): Promise<APIResponse<TrainingRecord[]>> =>
    get('/training', params),

  create: (data: Partial<TrainingRecord>): Promise<APIResponse<TrainingRecord>> =>
    post('/training', data),

  complete: (id: string, data: { score?: number; passed: boolean }): Promise<APIResponse<TrainingRecord>> =>
    put(`/training/${id}/complete`, data),

  gaps: (staffId: string): Promise<APIResponse<unknown>> =>
    get('/agents/track2/training/gaps', { staff_id: staffId }),
};
