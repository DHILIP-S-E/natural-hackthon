import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { Calendar, Users, BookOpen, Star, Activity, AlertTriangle, ArrowUpRight, ArrowDownRight, DollarSign } from 'lucide-react';
import { TiltCard } from '../../components/ui/TiltCard';
import { InlineSparkle } from '../../components/ui/PremiumBadge';
import api from '../../config/api';
import { ARCH_DATA } from '../../constants/archetypes';

const ICON_MAP: Record<string, any> = { DollarSign, BookOpen, Star, Activity };
const STATUS_COLORS: Record<string, string> = { checked_in: 'var(--success)', confirmed: 'var(--teal)', pending: 'var(--warning)', in_progress: 'var(--gold)', completed: 'var(--success)' };

export default function ManagerDashboard() {
  const { data: overview } = useQuery({
    queryKey: ['analytics', 'overview'],
    queryFn: () => api.get('/analytics/overview').then(r => r.data?.data),
  });

  const { data: bookingsRaw } = useQuery({
    queryKey: ['bookings', 'today'],
    queryFn: () => api.get('/bookings/today').then(r => {
      const d = r.data?.data;
      return Array.isArray(d) ? d : d?.bookings || d?.items || [];
    }),
  });

  const { data: staffData } = useQuery({
    queryKey: ['analytics-staff-dashboard'],
    queryFn: () => api.get('/analytics/staff').then(r => r.data?.data),
  });

  const { data: climateData } = useQuery({
    queryKey: ['climate-dashboard'],
    queryFn: () => api.get('/climate/').then(r => r.data?.data).catch(() => null),
  });

  const { data: soulskinData } = useQuery({
    queryKey: ['analytics-soulskin-dashboard'],
    queryFn: () => api.get('/analytics/soulskin').then(r => r.data?.data),
  });

  // Build KPI data from API
  const revenue = Number(overview?.total_revenue) || 0;
  const totalBookings = Number(overview?.total_bookings) || 0;
  const avgQuality = Number(overview?.avg_quality_score) || 0;
  const soulskinSessions = Number(overview?.soulskin_sessions) || 0;

  const kpiData = [
    { label: 'Revenue', value: `₹${Math.round(revenue).toLocaleString()}`, change: `${totalBookings} bookings`, positive: revenue > 0, icon: 'DollarSign', color: '#f44f9a' },
    { label: 'Bookings', value: totalBookings.toString(), change: `${overview?.completed_bookings || 0} completed`, positive: true, icon: 'BookOpen', color: '#2A9D8F' },
    { label: 'Quality Score', value: (avgQuality / 20).toFixed(1), change: avgQuality >= 80 ? 'Excellent' : 'Good', positive: avgQuality >= 70, icon: 'Star', color: '#9B7FD4' },
    { label: 'SOULSKIN', value: soulskinSessions.toString(), change: 'sessions', positive: soulskinSessions > 0, icon: 'Activity', color: '#9B7FD4' },
  ];

  // Map bookings to display format
  const todayBookings = Array.isArray(bookingsRaw) ? bookingsRaw : [];
  const upcoming = todayBookings.map((b: any) => {
    const schedDate = b.scheduled_at ? new Date(b.scheduled_at) : null;
    const timeStr = schedDate ? schedDate.toLocaleTimeString('en-IN', { hour: 'numeric', minute: '2-digit', hour12: true }) : '';
    return {
      time: timeStr,
      customer: b.customer_name || `Booking #${b.booking_number || ''}`,
      service: b.service_name || 'Service',
      stylist: b.stylist_name || '',
      archetype: b.archetype || null,
      status: b.status || 'confirmed',
    };
  });

  // Build alerts from climate data
  const alerts: any[] = [];
  if (climateData?.is_alert) {
    const hairAlerts = climateData.hair_recommendations?.alerts || [];
    const skinAlerts = climateData.skin_recommendations?.alerts || [];
    [...hairAlerts, ...skinAlerts].forEach((a: string) => {
      alerts.push({ type: 'climate', msg: a, severity: 'warning' });
    });
  }
  if (alerts.length === 0) {
    alerts.push({ type: 'info', msg: 'No active alerts — normal conditions', severity: 'info' });
  }

  // Build team data from staff API
  const team = (staffData?.staff || []).slice(0, 4).map((s: any) => ({
    name: s.name || 'Staff',
    role: s.skill_level || 'Stylist',
    completed: s.total_services || 0,
    inProgress: 0,
    rating: s.current_rating || 0,
    soulskin: s.soulskin_certified || false,
  }));

  // SOULSKIN archetype distribution
  const archetypeDist = soulskinData?.archetype_distribution || {};

  const now = new Date();
  const dateStr = now.toLocaleDateString('en-IN', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xl)' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem' }}>Manager Dashboard</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{dateStr}</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <span className="badge badge-success">Open</span>
          <span className="badge badge-teal">SOULSKIN Active</span>
        </div>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 'var(--space-md)' }}>
        {kpiData.map((kpi, i) => {
          const Icon = ICON_MAP[kpi.icon] || DollarSign;
          return (
            <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
              <TiltCard className="kpi-card" style={{ borderLeft: `4px solid ${kpi.color}`, padding: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
                  <span className="kpi-label" style={{ fontWeight: 600, letterSpacing: '0.05em' }}>{kpi.label}</span>
                  <div style={{ width: 32, height: 32, borderRadius: 8, background: `${kpi.color}12`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Icon size={16} color={kpi.color} />
                  </div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                  <span className="kpi-value" style={{ fontSize: '1.5rem', fontWeight: 700 }}>{kpi.value}</span>
                  <span className={`kpi-change ${kpi.positive ? 'positive' : 'negative'}`} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: '0.75rem', fontWeight: 600 }}>
                    {kpi.positive ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                    {kpi.change}
                  </span>
                </div>
              </TiltCard>
            </motion.div>
          );
        })}
      </div>

      {/* Main grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--space-lg)' }}>
        {/* Upcoming bookings */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
          <TiltCard tiltIntensity={3} className="card" style={{ overflow: 'hidden', padding: 0, height: '100%' }}>
            <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '1rem' }}><Calendar size={18} /> Today's Bookings</h4>
              <span className="badge badge-teal" style={{ fontWeight: 600 }}>{upcoming.length} total</span>
            </div>
            <div>
              {upcoming.length > 0 ? upcoming.map((b: any, i: number) => {
                const arch = b.archetype ? ARCH_DATA[b.archetype] : null;
                const ArchIcon = arch?.icon;
                const statusColor = STATUS_COLORS[b.status] || 'var(--text-muted)';
                return (
                  <div key={i} style={{ padding: '14px 20px', borderBottom: i < upcoming.length - 1 ? '1px solid var(--border-subtle)' : 'none', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-muted)', width: 75, fontWeight: 500 }}>{b.time}</span>
                      <div>
                        <div style={{ fontSize: '0.9rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 10 }}>
                          {b.customer}
                          {ArchIcon && (
                            <div style={{ width: 22, height: 22, borderRadius: 5, background: `${arch.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                              <ArchIcon size={12} color={arch.color} strokeWidth={2.5} />
                            </div>
                          )}
                        </div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>{b.service}{b.stylist ? ` · ${b.stylist}` : ''}</div>
                      </div>
                    </div>
                    <span style={{ fontSize: '0.65rem', color: statusColor, fontWeight: 700, letterSpacing: '0.05em', background: `${statusColor}15`, padding: '3px 8px', borderRadius: 4, textTransform: 'uppercase' }}>{(b.status || '').replace('_', ' ')}</span>
                  </div>
                );
              }) : (
                <div style={{ padding: 32, textAlign: 'center', color: 'var(--text-muted)' }}>No bookings for today</div>
              )}
            </div>
          </TiltCard>
        </motion.div>

        {/* Alerts panel */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }} className="card" style={{ padding: 0, display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
            <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><AlertTriangle size={18} /> Smart Alerts</h4>
          </div>
          <div style={{ flex: 1 }}>
            {alerts.map((a: any, i: number) => (
              <div key={i} style={{ padding: '14px 20px', borderBottom: '1px solid var(--border-subtle)', display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                <div style={{ width: 6, height: 6, borderRadius: '50%', marginTop: 6, background: a.severity === 'warning' ? 'var(--warning)' : 'var(--info)', flexShrink: 0 }} />
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{a.msg}</p>
              </div>
            ))}
          </div>

          {/* SOULSKIN quick stat */}
          <div style={{ padding: '20px', borderTop: '1px solid var(--border-subtle)', background: 'rgba(155,127,212,0.04)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--violet)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                <InlineSparkle /> SOULSKIN Today
              </span>
            </div>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {Object.entries(ARCH_DATA).map(([key, data]) => {
                const Icon = data.icon;
                const count = archetypeDist[key] || 0;
                return (
                  <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 6, background: '#fff', border: '1px solid var(--border-subtle)', padding: '5px 12px', borderRadius: 'var(--radius-full)', fontSize: '0.75rem', fontWeight: 600 }}>
                    <Icon size={12} color={data.color} strokeWidth={2.5} />
                    <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>{count}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Staff performance strip */}
      {team.length > 0 && (
        <div className="card" style={{ padding: 0 }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
            <h4 style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Users size={18} /> Team</h4>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 0 }}>
            {team.map((s: any, i: number) => (
              <div key={i} style={{ padding: '16px 20px', borderRight: '1px solid var(--border-subtle)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
                  <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'var(--bg-surface)', border: '2px solid var(--border-medium)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600, fontSize: '0.8rem', color: 'var(--gold)' }}>
                    {(s.name ?? '').split(' ').map((n: string) => n[0]).join('').substring(0, 2)}
                  </div>
                  <div>
                    <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{s.name}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{s.role}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 12, fontSize: '0.75rem' }}>
                  <div><span style={{ color: 'var(--success)', fontWeight: 600 }}>{s.completed}</span> <span style={{ color: 'var(--text-muted)' }}>services</span></div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <Star size={12} style={{ color: 'var(--gold)' }} /><span style={{ fontWeight: 600 }}>{s.rating?.toFixed(1) || '0'}</span>
                  </div>
                  {s.soulskin && <span style={{ color: 'var(--violet)', fontSize: '0.7rem' }}>✨ SOULSKIN</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
