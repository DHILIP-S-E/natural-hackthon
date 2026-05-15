import { get } from '../base/api_base';
import type { APIResponse } from '../base/base_type';
import type { Service } from '../../types/service/service_types';

export const servicesApi = {
  list: (params?: { category?: string; is_active?: boolean }): Promise<APIResponse<Service[]>> =>
    get('/services', params),

  getById: (id: string): Promise<APIResponse<Service>> =>
    get(`/services/${id}`),

  categories: (): Promise<APIResponse<string[]>> =>
    get('/services/categories'),
};
