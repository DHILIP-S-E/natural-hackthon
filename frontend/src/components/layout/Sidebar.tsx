import { NavLink, useNavigate, Outlet } from 'react-router-dom';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuthStore, getRoleLabel } from '../../stores/authStore';
import ErrorBoundary from '../ErrorBoundary';
import {
  LayoutDashboard, Calendar, Users, BookOpen, BarChart3, Star,
  TrendingUp, MessageSquare, Bell, Settings, LogOut, ChevronLeft,
  Sparkles, ClipboardList, GraduationCap, Users2, GitCompare,
  Map, Shield, Brain, Activity, Home, BookOpenCheck, Scan,
  Heart, Palette, Route, User
} from 'lucide-react';
import type { UserRole } from '../../types';

interface NavItem {
  to: string;
  icon: React.ReactNode;
  label: string;
  roles?: UserRole[];
}

const navItems: Record<string, NavItem[]> = {
  customer: [
    { to: '/app/dashboard', icon: <Home size={20} />, label: 'Home' },
    { to: '/app/passport', icon: <BookOpenCheck size={20} />, label: 'Passport' },
    { to: '/app/mirror', icon: <Scan size={20} />, label: 'Mirror' },
    { to: '/app/bookings', icon: <Calendar size={20} />, label: 'Bookings' },
    { to: '/app/journey', icon: <Route size={20} />, label: 'Journey' },
    { to: '/app/soulskin', icon: <Sparkles size={20} />, label: 'SOULSKIN' },
    { to: '/app/homecare', icon: <Heart size={20} />, label: 'Homecare' },
    { to: '/app/profile', icon: <User size={20} />, label: 'Profile' },
  ],
  stylist: [
    { to: '/stylist/dashboard', icon: <LayoutDashboard size={20} />, label: 'Today' },
    { to: '/stylist/customers', icon: <Users size={20} />, label: 'Customers' },
    { to: '/stylist/performance', icon: <BarChart3 size={20} />, label: 'Performance' },
    { to: '/stylist/training', icon: <GraduationCap size={20} />, label: 'Training' },
  ],
  salon_manager: [
    { to: '/manager/dashboard', icon: <LayoutDashboard size={20} />, label: 'Dashboard' },
    { to: '/manager/today', icon: <Calendar size={20} />, label: 'Today' },
    { to: '/manager/team', icon: <Users size={20} />, label: 'Team' },
    { to: '/manager/bookings', icon: <BookOpen size={20} />, label: 'Bookings' },
    { to: '/manager/queue', icon: <Users2 size={20} />, label: 'Queue' },
    { to: '/manager/quality', icon: <Star size={20} />, label: 'Quality' },
    { to: '/manager/soulskin', icon: <Sparkles size={20} />, label: 'SOULSKIN' },
    { to: '/manager/sops', icon: <ClipboardList size={20} />, label: 'SOPs' },
    { to: '/manager/trends', icon: <TrendingUp size={20} />, label: 'Trends' },
    { to: '/manager/reports', icon: <BarChart3 size={20} />, label: 'Reports' },
    { to: '/manager/feedback', icon: <MessageSquare size={20} />, label: 'Feedback' },
    { to: '/manager/alerts', icon: <Bell size={20} />, label: 'Alerts' },
  ],
  franchise_owner: [
    { to: '/franchise/dashboard', icon: <LayoutDashboard size={20} />, label: 'Dashboard' },
    { to: '/franchise/locations', icon: <Map size={20} />, label: 'Locations' },
    { to: '/franchise/revenue', icon: <BarChart3 size={20} />, label: 'Revenue' },
    { to: '/franchise/quality', icon: <Star size={20} />, label: 'Quality' },
    { to: '/franchise/staff', icon: <Users size={20} />, label: 'Staff' },
    { to: '/franchise/compare', icon: <GitCompare size={20} />, label: 'Compare' },
    { to: '/franchise/reports', icon: <ClipboardList size={20} />, label: 'Reports' },
  ],
  regional_manager: [
    { to: '/regional/dashboard', icon: <LayoutDashboard size={20} />, label: 'Dashboard' },
    { to: '/regional/map', icon: <Map size={20} />, label: 'Region Map' },
    { to: '/regional/locations', icon: <Map size={20} />, label: 'Locations' },
    { to: '/regional/revenue', icon: <BarChart3 size={20} />, label: 'Revenue' },
    { to: '/regional/quality', icon: <Star size={20} />, label: 'Quality' },
    { to: '/regional/staff', icon: <Users size={20} />, label: 'Staff' },
    { to: '/regional/trends', icon: <TrendingUp size={20} />, label: 'Trends' },
    { to: '/regional/reports', icon: <ClipboardList size={20} />, label: 'Reports' },
  ],
  super_admin: [
    { to: '/admin/dashboard', icon: <LayoutDashboard size={20} />, label: 'Command Center' },
    { to: '/admin/map', icon: <Map size={20} />, label: 'Network Map' },
    { to: '/admin/locations', icon: <Map size={20} />, label: 'Locations' },
    { to: '/admin/users', icon: <Users size={20} />, label: 'Users' },
    { to: '/admin/revenue', icon: <BarChart3 size={20} />, label: 'Revenue' },
    { to: '/admin/quality', icon: <Star size={20} />, label: 'Quality' },
    { to: '/admin/trends', icon: <TrendingUp size={20} />, label: 'Trends' },
    { to: '/admin/ai', icon: <Brain size={20} />, label: 'AI Engine' },
    { to: '/admin/soulskin', icon: <Sparkles size={20} />, label: 'SOULSKIN' },
    { to: '/admin/bi', icon: <Activity size={20} />, label: 'BI Dashboard' },
    { to: '/admin/training', icon: <GraduationCap size={20} />, label: 'Training' },
    { to: '/admin/config', icon: <Settings size={20} />, label: 'Config' },
    { to: '/admin/rbac', icon: <Shield size={20} />, label: 'Roles & Audit' },
  ],
};

export default function Sidebar() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  if (!user) return null;

  const items = navItems[user.role] || [];

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <aside
      style={{
        width: collapsed ? 'var(--sidebar-collapsed)' : 'var(--sidebar-width)',
        minHeight: '100vh',
        background: 'var(--bg-surface)',
        borderRight: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        transition: 'width var(--transition-base)',
        position: 'fixed',
        top: 0,
        left: 0,
        zIndex: 50,
        overflow: 'hidden',
      }}
    >
      {/* Logo */}
      <div style={{
        padding: collapsed ? '20px 12px' : '20px 20px',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <svg width="32" height="32" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ flexShrink: 0 }}>
            <rect width="40" height="40" rx="8" fill="#f44f9a" />
            <path d="M20 8L10 28H14L20 15L26 28H30L20 8Z" fill="white" />
            <path d="M16 22H24" stroke="white" strokeWidth="2" strokeLinecap="round" />
          </svg>
          {!collapsed && <span style={{ fontFamily: 'var(--font-display)', fontSize: '1.4rem', fontWeight: 800, color: '#1A1A24', letterSpacing: '0.05em' }}>AURA</span>}
        </div>
        <button
          onClick={() => setCollapsed(!collapsed)}
          style={{
            background: 'none', border: 'none', color: 'var(--text-muted)',
            cursor: 'pointer', padding: 4, display: 'flex',
          }}
        >
          <ChevronLeft size={18} style={{ transform: collapsed ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
        </button>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, padding: '12px 8px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '2px' }}>
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            style={({ isActive }) => ({
              display: 'flex', alignItems: 'center', gap: '12px',
              padding: collapsed ? '10px 12px' : '10px 14px',
              borderRadius: 'var(--radius-md)',
              color: isActive ? '#f44f9a' : 'var(--text-secondary)',
              background: isActive ? 'rgba(244,79,154,0.06)' : 'transparent',
              textDecoration: 'none', fontSize: '0.85rem', fontWeight: isActive ? 700 : 500,
              transition: 'all var(--transition-fast)',
              whiteSpace: 'nowrap', overflow: 'hidden',
            })}
          >
            {item.icon}
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* User section */}
      <div style={{
        padding: collapsed ? '12px' : '16px',
        borderTop: '1px solid var(--border-subtle)',
        display: 'flex', flexDirection: 'column', gap: '8px',
      }}>
        {!collapsed && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: 36, height: 36, borderRadius: '50%',
              background: 'var(--bg-card)', border: '2px solid var(--border-medium)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '14px', fontWeight: 700, color: '#f44f9a',
            }}>
              {user.first_name[0]}{user.last_name[0]}
            </div>
            <div>
              <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{user.first_name} {user.last_name}</div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{getRoleLabel(user.role)}</div>
            </div>
          </div>
        )}
        <button
          onClick={handleLogout}
          style={{
            display: 'flex', alignItems: 'center', justifyContent: collapsed ? 'center' : 'flex-start',
            gap: '10px', padding: '8px 12px', borderRadius: 'var(--radius-md)',
            background: 'none', border: 'none', color: 'var(--text-muted)',
            cursor: 'pointer', fontSize: '0.8rem', width: '100%',
          }}
        >
          <LogOut size={16} />
          {!collapsed && 'Sign Out'}
        </button>
      </div>
    </aside>
  );
}

/* Dashboard Layout — sidebar + main content */
export function DashboardLayout() {
  const [sidebarCollapsed] = useState(false);

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <main style={{
        flex: 1,
        marginLeft: sidebarCollapsed ? 'var(--sidebar-collapsed)' : 'var(--sidebar-width)',
        padding: 'var(--space-xl)',
        transition: 'margin-left var(--transition-base)',
        maxWidth: '100%',
        overflow: 'hidden',
      }}>
        <AnimatePresence mode="wait">
          <motion.div
            key={window.location.pathname}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
          >
            <ErrorBoundary>
              <Outlet />
            </ErrorBoundary>
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
