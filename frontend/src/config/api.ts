import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
});

// Supabase client for direct storage/auth if needed
export const supabaseConfig = {
  url: import.meta.env.VITE_SUPABASE_URL || '',
  anonKey: import.meta.env.VITE_SUPABASE_ANON_KEY || '',
};

// Request interceptor — attach JWT
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('aura_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Token refresh state — prevents concurrent refresh race condition
let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

function onTokenRefreshed(token: string) {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
}

function addRefreshSubscriber(cb: (token: string) => void) {
  refreshSubscribers.push(cb);
}

// Response interceptor — handle 401 with token refresh (race-safe)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (isRefreshing) {
        // Another request is already refreshing — wait for it
        return new Promise((resolve) => {
          addRefreshSubscriber((newToken: string) => {
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            resolve(api(originalRequest));
          });
        });
      }

      isRefreshing = true;
      const refreshToken = localStorage.getItem('aura_refresh_token');

      if (refreshToken) {
        try {
          const resp = await axios.post(
            `${originalRequest.baseURL}/auth/refresh`,
            null,
            { params: { token: refreshToken }, timeout: 10000 }
          );
          if (resp.data?.success && resp.data?.data?.access_token) {
            const newToken = resp.data.data.access_token;
            localStorage.setItem('aura_token', newToken);
            localStorage.setItem('aura_refresh_token', resp.data.data.refresh_token);
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            isRefreshing = false;
            onTokenRefreshed(newToken);
            return api(originalRequest);
          }
        } catch {
          // Refresh failed — force logout
        }
      }

      isRefreshing = false;
      refreshSubscribers = [];
      localStorage.removeItem('aura_token');
      localStorage.removeItem('aura_refresh_token');
      localStorage.removeItem('aura_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
