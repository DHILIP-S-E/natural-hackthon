import { get, post } from '../base/api_base';
import type { APIResponse } from '../base/base_type';
import type { User, TokenResponse } from '../../types/user/user_types';

export const authApi = {
  login: (email: string, password: string): Promise<APIResponse<TokenResponse>> =>
    post('/auth/login', { email, password }),

  register: (data: {
    email: string; password: string; first_name: string; last_name: string;
    role?: string; phone?: string;
  }): Promise<APIResponse<TokenResponse>> =>
    post('/auth/register', data),

  refresh: (token: string): Promise<APIResponse<{ access_token: string; refresh_token: string }>> =>
    (post as any)('/auth/refresh', null, { params: { token } }),

  me: (): Promise<APIResponse<User>> =>
    get('/auth/me'),

  logout: (): Promise<APIResponse<null>> =>
    post('/auth/logout'),
};
