import { create } from 'zustand';
import type { User, UserRole } from '../types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: (() => {
    try { return JSON.parse(localStorage.getItem('aura_user') || 'null'); } catch { return null; }
  })(),
  token: localStorage.getItem('aura_token'),
  isAuthenticated: !!localStorage.getItem('aura_token'),

  login: (token, user) => {
    localStorage.setItem('aura_token', token);
    localStorage.setItem('aura_user', JSON.stringify(user));
    set({ token, user, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('aura_token');
    localStorage.removeItem('aura_user');
    set({ token: null, user: null, isAuthenticated: false });
  },

  updateUser: (updates) => set((state) => {
    const user = state.user ? { ...state.user, ...updates } : null;
    if (user) localStorage.setItem('aura_user', JSON.stringify(user));
    return { user };
  }),
}));

// Role-based helpers
export const getRoleRedirect = (role: UserRole): string => {
  const routes: Record<UserRole, string> = {
    customer: '/app/dashboard',
    stylist: '/stylist/dashboard',
    salon_manager: '/manager/dashboard',
    franchise_owner: '/franchise/dashboard',
    regional_manager: '/regional/dashboard',
    super_admin: '/admin/dashboard',
  };
  return routes[role] || '/';
};

export const getRoleLabel = (role: UserRole): string => {
  const labels: Record<UserRole, string> = {
    super_admin: 'Super Admin',
    regional_manager: 'Regional Manager',
    franchise_owner: 'Franchise Owner',
    salon_manager: 'Salon Manager',
    stylist: 'Stylist',
    customer: 'Customer',
  };
  return labels[role] || role;
};
