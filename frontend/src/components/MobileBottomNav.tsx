import { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import {
  Home, BookOpenCheck, Scan, Calendar, Route,
  LayoutDashboard, ClipboardList, Users, BarChart3, GraduationCap,
} from 'lucide-react';
import { useAuthStore } from '../stores/authStore';

interface NavTab {
  to: string;
  icon: React.ReactNode;
  label: string;
}

const customerTabs: NavTab[] = [
  { to: '/app/dashboard', icon: <Home size={22} />, label: 'Home' },
  { to: '/app/passport', icon: <BookOpenCheck size={22} />, label: 'Passport' },
  { to: '/app/mirror', icon: <Scan size={22} />, label: 'Mirror' },
  { to: '/app/bookings', icon: <Calendar size={22} />, label: 'Bookings' },
  { to: '/app/journey', icon: <Route size={22} />, label: 'Journey' },
];

const stylistTabs: NavTab[] = [
  { to: '/stylist/dashboard', icon: <LayoutDashboard size={22} />, label: 'Today' },
  { to: '/stylist/session', icon: <ClipboardList size={22} />, label: 'Session' },
  { to: '/stylist/customers', icon: <Users size={22} />, label: 'Customers' },
  { to: '/stylist/performance', icon: <BarChart3 size={22} />, label: 'Growth' },
  { to: '/stylist/training', icon: <GraduationCap size={22} />, label: 'Training' },
];

export default function MobileBottomNav() {
  const { user } = useAuthStore();
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  if (!isMobile || !user) return null;

  const tabs = user.role === 'stylist' ? stylistTabs : customerTabs;

  return (
    <nav
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        height: 60,
        zIndex: 100,
        background: 'var(--bg-elevated)',
        borderTop: '1px solid var(--border-subtle)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-around',
        paddingBottom: 'env(safe-area-inset-bottom, 0px)',
        boxShadow: '0 -2px 12px rgba(0, 0, 0, 0.06)',
      }}
    >
      {tabs.map((tab) => (
        <NavLink
          key={tab.to}
          to={tab.to}
          style={({ isActive }) => ({
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '2px',
            flex: 1,
            height: '100%',
            textDecoration: 'none',
            color: isActive ? 'var(--gold)' : 'var(--text-muted)',
            fontSize: '0.65rem',
            fontFamily: 'var(--font-body)',
            fontWeight: isActive ? 700 : 500,
            transition: 'color var(--transition-fast)',
          })}
        >
          {tab.icon}
          <span>{tab.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
