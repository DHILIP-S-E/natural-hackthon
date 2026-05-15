import { get, put } from '../base/api_base';
import type { APIResponse } from '../base/base_type';
import type { CustomerProfile } from '../../types/customer/customer_types';

export const customersApi = {
  me: (): Promise<APIResponse<CustomerProfile>> =>
    get('/customers/me'),

  getById: (id: string): Promise<APIResponse<CustomerProfile>> =>
    get(`/customers/${id}`),

  list: (params?: { limit?: number; offset?: number }): Promise<APIResponse<CustomerProfile[]>> =>
    get('/customers', params),

  updateProfile: (data: Partial<CustomerProfile>): Promise<APIResponse<CustomerProfile>> =>
    put('/customers/me', data),

  passport: (customerId: string): Promise<APIResponse<CustomerProfile>> =>
    get(`/agents/track3/passport/full`, { customer_id: customerId }),

  nextBestActions: (customerId: string): Promise<APIResponse<unknown>> =>
    get(`/agents/track3/recommendations/next-best`, { customer_id: customerId }),
};
