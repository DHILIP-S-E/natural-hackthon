import type { APIResponse } from './base_type';
import { APIError } from './errors';

export function unwrap<T>(response: APIResponse<T>): T {
  if (!response.success || response.data === null || response.data === undefined) {
    throw new APIError(400, response.message ?? 'Request failed');
  }
  return response.data;
}
