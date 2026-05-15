import { get, put } from '../base/api_base';
import type { APIResponse } from '../base/base_type';
import type { Notification } from '../../types/notification/notification_types';

export const notificationsApi = {
  list: (params?: { unread_only?: boolean; limit?: number }): Promise<APIResponse<Notification[]>> =>
    get('/notifications', params),

  markRead: (id: string): Promise<APIResponse<null>> =>
    put(`/notifications/${id}/read`, {}),

  markAllRead: (): Promise<APIResponse<null>> =>
    put('/notifications/read-all', {}),
};
