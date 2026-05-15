/**
 * Thin axios wrapper — all domain api files import from here.
 * Pages and components import ONLY from hooks/, never from this file directly.
 */
import axios from 'axios';
import type { APIResponse } from './base_type';

const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

// Attach JWT on every request
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('aura_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Race-safe token refresh on 401
let isRefreshing = false;
let subscribers: ((token: string) => void)[] = [];

function broadcast(token: string) {
  subscribers.forEach((cb) => cb(token));
  subscribers = [];
}

http.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      if (isRefreshing) {
        return new Promise((resolve) => {
          subscribers.push((token) => {
            original.headers.Authorization = `Bearer ${token}`;
            resolve(http(original));
          });
        });
      }
      isRefreshing = true;
      const refresh = localStorage.getItem('aura_refresh_token');
      if (refresh) {
        try {
          const resp = await axios.post(
            `${original.baseURL}/auth/refresh`,
            null,
            { params: { token: refresh }, timeout: 10000 },
          );
          if (resp.data?.success && resp.data?.data?.access_token) {
            const newToken = resp.data.data.access_token;
            localStorage.setItem('aura_token', newToken);
            localStorage.setItem('aura_refresh_token', resp.data.data.refresh_token ?? refresh);
            original.headers.Authorization = `Bearer ${newToken}`;
            isRefreshing = false;
            broadcast(newToken);
            return http(original);
          }
        } catch {
          // refresh failed — fall through to logout
        }
      }
      isRefreshing = false;
      subscribers = [];
      localStorage.removeItem('aura_token');
      localStorage.removeItem('aura_refresh_token');
      localStorage.removeItem('aura_user');
      window.location.href = '/login';
    }
    const message = error.response?.data?.message ?? error.message;
    return Promise.reject(new Error(message));
  },
);

export async function get<T>(url: string, params?: object): Promise<APIResponse<T>> {
  const res = await http.get<APIResponse<T>>(url, { params });
  return res.data;
}

export async function post<T>(url: string, body?: object): Promise<APIResponse<T>> {
  const res = await http.post<APIResponse<T>>(url, body);
  return res.data;
}

export async function put<T>(url: string, body?: object): Promise<APIResponse<T>> {
  const res = await http.put<APIResponse<T>>(url, body);
  return res.data;
}

export async function patch<T>(url: string, body?: object): Promise<APIResponse<T>> {
  const res = await http.patch<APIResponse<T>>(url, body);
  return res.data;
}

export async function del<T>(url: string): Promise<APIResponse<T>> {
  const res = await http.delete<APIResponse<T>>(url);
  return res.data;
}

export default http;
