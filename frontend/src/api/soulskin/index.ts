import { get, post, put } from '../base/api_base';
import type { APIResponse } from '../base/base_type';
import type { SoulskinSession } from '../../types/soulskin/soulskin_types';

export const soulskinApi = {
  create: (data: { booking_id?: string; customer_id: string }): Promise<APIResponse<SoulskinSession>> =>
    post('/soulskin/sessions', data),

  getById: (id: string): Promise<APIResponse<SoulskinSession>> =>
    get(`/soulskin/sessions/${id}`),

  answer: (id: string, answers: { question_1_song?: string; question_2_colour?: string; question_3_word?: string }): Promise<APIResponse<SoulskinSession>> =>
    put(`/soulskin/sessions/${id}/answers`, answers),

  complete: (id: string): Promise<APIResponse<SoulskinSession>> =>
    put(`/soulskin/sessions/${id}/complete`, {}),

  myHistory: (): Promise<APIResponse<SoulskinSession[]>> =>
    get('/soulskin/me/history'),

  protocol: (sessionId: string): Promise<APIResponse<unknown>> =>
    get(`/agents/track3/soulskin/protocol`, { session_id: sessionId }),
};
