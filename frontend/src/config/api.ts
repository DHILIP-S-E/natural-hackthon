import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: { 'Content-Type': 'application/json' },
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

// Response interceptor — handle 401 with token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Try refresh token on 401 (but not if already retrying)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('aura_refresh_token');

      if (refreshToken) {
        try {
          const resp = await axios.post(
            `${originalRequest.baseURL}/auth/refresh`,
            null,
            { params: { token: refreshToken } }
          );
          if (resp.data?.success && resp.data?.data?.access_token) {
            localStorage.setItem('aura_token', resp.data.data.access_token);
            localStorage.setItem('aura_refresh_token', resp.data.data.refresh_token);
            originalRequest.headers.Authorization = `Bearer ${resp.data.data.access_token}`;
            return api(originalRequest);
          }
        } catch {
          // Refresh failed — force logout
        }
      }

      localStorage.removeItem('aura_token');
      localStorage.removeItem('aura_refresh_token');
      localStorage.removeItem('aura_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
