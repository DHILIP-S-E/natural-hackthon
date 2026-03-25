import { motion, AnimatePresence } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { Calendar, Users, BookOpen, Star, Activity, AlertTriangle, ArrowUpRight, ArrowDownRight, DollarSign, Clock, ShieldCheck, Zap, TrendingUp, ChevronRight } from 'lucide-react';
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
    queryKey: ['analytics', 'staff'],
    queryFn: () => api.get('/analytics/staff').then(r => r.data?.data),
    staleTime: 5 * 60 * 1000,
  });

  const { data: climateData } = useQuery({
    queryKey: ['climate', 'dashboard'],
    queryFn: () => api.get('/climate/').then(r => r.data?.data).catch(() => null),
    staleTime: 10 * 60 * 1000,
  });

  const { data: soulskinData } = useQuery({
    queryKey: ['analytics', 'soulskin'],
    queryFn: () => api.get('/analytics/soulskin').then(r => r.data?.data),
    staleTime: 5 * 60 * 1000,
  });

  const { data: timeMonitor } = useQuery({
    queryKey: ['quality', 'time-monitor'],
    queryFn: () => api.get('/quality/agents/time-monitor?location_id=L-001').then(r => r.data?.data), // Hardcoded Loc for demo
    refetchInterval: 30000,
  });

  const { data: benchmarkData } = useQuery({
    queryKey: ['quality', 'benchmark'],
    queryFn: () => api.get('/quality/agents/benchmark').then(r => r.data?.data),
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

  // Operational Health Metrics
  const healthMetrics = [
    { label: 'Rushing Risk', value: timeMonitor?.rushing_count || 0, color: 'var(--warning)', icon: Zap },
    { label: 'Overtime', value: timeMonitor?.overtime_count || 0, color: 'var(--rose)', icon: Clock },
    { label: 'Compliance', value: `${(overview?.avg_sop_compliance || 0).toFixed(0)}%`, color: 'var(--teal)', icon: ShieldCheck },
  ];

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
      </div>

      {/* AI Operational Health Section */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--space-lg)' }}>
        {healthMetrics.map((m, i) => (
          <motion.div key={i} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.1 }}
            className="card" style={{ padding: '20px', display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{ width: 44, height: 44, borderRadius: 12, background: `${m.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <m.icon size={22} color={m.color} />
            </div>
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{m.label}</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>{m.value}</div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Team Coaching & Onboarding Insights */}
      <div className="card" style={{ padding: 0, position: 'relative', overflow: 'hidden' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid var(--border-subtle)', background: 'linear-gradient(90deg, rgba(42,157,143,0.05) 0%, rgba(255,255,255,0) 100%)' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 10 }}>
            <Zap size={18} color="var(--gold)" /> AI Team Coaching: Upsell & Readiness
          </h3>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 0 }}>
          {team.map((s: any, i: number) => (
            <div key={i} style={{ padding: '24px', borderRight: i % 2 === 0 ? '1px solid var(--border-subtle)' : 'none', borderBottom: i < team.length - 2 ? '1px solid var(--border-subtle)' : 'none' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                <div style={{ display: 'flex', gap: 12 }}>
                  <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--bg-surface)', border: '2px solid var(--border-medium)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.8rem', color: 'var(--gold)' }}>
                    {s.name.split(' ').map((n: string) => n[0]).join('')}
                  </div>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>{s.name}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{s.role} · {s.rating.toFixed(1)} ★</div>
                  </div>
                </div>
                <div className="badge badge-success" style={{ fontSize: '0.65rem' }}>Active</div>
              </div>

              {/* Training Progress (Onboarding Agent proxy) */}
              <div style={{ marginBottom: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', marginBottom: 6 }}>
                  <span style={{ color: 'var(--text-secondary)' }}>Skill Readiness (L2)</span>
                  <span style={{ fontWeight: 600 }}>{70 + i * 5}%</span>
                </div>
                <div style={{ height: 4, background: 'var(--bg-surface)', borderRadius: 2 }}>
                  <div style={{ height: '100%', width: `${70 + i * 5}%`, background: 'var(--teal)', borderRadius: 2 }} />
                </div>
              </div>

              {/* AI Suggestion */}
              <div style={{ padding: 12, background: 'rgba(155,127,212,0.06)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(155,127,212,0.1)' }}>
                <div style={{ fontSize: '0.65rem', color: 'var(--violet)', fontWeight: 700, marginBottom: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
                  <TrendingUp size={12} /> UPSELL OPPORTUNITY
                </div>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  {i % 2 === 0 ? 'Recommend Soulskin Hydration for current guest.' : 'Bundle Scalp Detox with upcoming Hair Spa.'}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
